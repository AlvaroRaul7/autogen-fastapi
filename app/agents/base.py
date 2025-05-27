from abc import ABC, abstractmethod
import autogen
from typing import List, Dict, Any, Optional
from app.core.config import get_settings
from app.core.logging import autogen_logger

settings = get_settings()

class BaseAgent(ABC):
    """
    Base class for all custom agents in the application.
    Provides common functionality and required interface for agent implementations.
    """
    
    def __init__(self):
        self.logger = autogen_logger
        self.logger.info(f"Initializing {self.__class__.__name__}")
        
        self.config_list = [
            {
                "model": settings.COMPLETION_MODEL,
                "api_key": settings.OPENAI_API_KEY,
            }
        ]
        
        self.logger.debug(f"Agent configuration: {self.config_list}")
        
        # Initialize the user proxy agent that will be used by all agents
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=int(settings.MAX_CONSECUTIVE_REPLIES),
            code_execution_config=False,
            llm_config={
                "config_list": self.config_list,
                "temperature": settings.AGENT_TEMPERATURE,
            }
        )
        
        self.logger.info("User proxy agent initialized")
        
        # Initialize specialized agents
        self.agents = self._initialize_agents()
        self.logger.info(f"Initialized {len(self.agents)} specific agents")
    
    @abstractmethod
    def _initialize_agents(self) -> Dict[str, autogen.AssistantAgent]:
        """
        Initialize the specialized agents needed for this agent type.
        Must be implemented by subclasses.
        
        Returns:
            Dict[str, autogen.AssistantAgent]: Dictionary of initialized agents
        """
        pass
    
    def _create_assistant_agent(
        self,
        name: str,
        system_message: str,
        temperature: Optional[float] = None
    ) -> autogen.AssistantAgent:
        """
        Create a new assistant agent with logging.
        
        Args:
            name: Name of the agent
            system_message: System message defining agent's role
            temperature: Optional temperature override
        
        Returns:
            autogen.AssistantAgent: Initialized assistant agent
        """
        self.logger.info(f"Creating assistant agent: {name}")
        self.logger.debug(f"System message for {name}: {system_message}")
        
        agent = autogen.AssistantAgent(
            name=name,
            system_message=system_message,
            llm_config={
                "config_list": self.config_list,
                "temperature": temperature or settings.AGENT_TEMPERATURE,
            }
        )
        
        self.logger.info(f"Assistant agent {name} created successfully")
        return agent
    
    async def process(self, operation: str, **kwargs) -> Any:
        """
        Process an operation using the appropriate agents.
        
        Args:
            operation: The type of operation to perform
            **kwargs: Additional arguments for the operation
            
        Returns:
            Any: The result of the operation
        """
        self.logger.info(f"Processing operation: {operation}")
        try:
            result = await self._process_operation(operation, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Error during operation {operation}: {str(e)}", exc_info=True)
            raise
    
    @abstractmethod
    async def _process_operation(self, operation: str, **kwargs) -> Any:
        """
        Process a specific operation using the agents.
        Must be implemented by child classes.
        
        Args:
            operation: Name of the operation to perform
            **kwargs: Additional arguments for the operation
        
        Returns:
            Any: Result of the operation
        """
        pass
    
    def _get_agent_response(
        self,
        agent: autogen.AssistantAgent,
        message: str,
        silent: bool = True
    ) -> str:
        """
        Get a response from an agent through the user proxy.
        
        Args:
            agent: The agent to get a response from
            message: The message to send to the agent
            silent: Whether to suppress intermediate chat messages
            
        Returns:
            str: The agent's response
        """
        try:
            # Initiate the chat and get the response
            response = self.user_proxy.initiate_chat(
                agent,
                message=message,
                silent=silent
            )
            
            # Extract the last assistant message
            last_message = None
            for msg in reversed(response.chat_history):
                if msg.get("role") == "assistant":
                    last_message = msg.get("content")
                    break
            
            if not last_message:
                raise ValueError("No response received from agent")
                
            return last_message
            
        except Exception as e:
            self.logger.error(f"Error getting agent response: {str(e)}", exc_info=True)
            raise