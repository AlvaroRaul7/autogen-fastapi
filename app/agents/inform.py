from typing import Dict, List, Any
import autogen
from app.agents.base import BaseAgent
from app.core.config import get_settings

settings = get_settings()

class InformAgent(BaseAgent):
    """
    An agent specialized in information processing and analysis.
    Combines a researcher for query enhancement and an analyst for document analysis.
    """
    
    def _initialize_agents(self) -> Dict[str, autogen.AssistantAgent]:
        """
        Initialize the researcher and analyst agents.
        
        Returns:
            Dict[str, autogen.AssistantAgent]: Dictionary containing both agents
        """
        self.logger.info("Initializing InformAgent's specialized agents")
        
        researcher = autogen.AssistantAgent(
            name="researcher",
            system_message="""You are a research assistant specialized in processing queries 
            and extracting key information requirements. Help formulate effective search queries 
            that capture the essential elements of the user's information needs.""",
            llm_config={
                "config_list": self.config_list,
                "temperature": settings.AGENT_TEMPERATURE,
            }
        )
        
        analyst = autogen.AssistantAgent(
            name="document_analyst",
            system_message="""You are an expert document analyst. Your role is to analyze 
            document chunks and provide detailed, accurate responses to queries. Focus on 
            extracting key information and presenting it in a clear, organized manner.""",
            llm_config={
                "config_list": self.config_list,
                "temperature": settings.AGENT_TEMPERATURE,
            }
        )
        
        return {
            "researcher": researcher,
            "analyst": analyst
        }
    
    async def _process_operation(self, operation: str, **kwargs) -> Any:
        """
        Process different types of operations using appropriate agents.
        
        Args:
            operation: Type of operation to perform
            **kwargs: Operation-specific arguments
            
        Returns:
            Any: Result of the operation
        """
        operations = {
            "enhance_query": self._enhance_query,
            "analyze_chunks": self._analyze_chunks
        }
        
        if operation not in operations:
            raise ValueError(f"Unknown operation: {operation}")
            
        return await operations[operation](**kwargs)
    
    async def _enhance_query(self, query: str) -> str:
        """
        Use the researcher agent to enhance a search query.
        
        Args:
            query: Original query to enhance
            
        Returns:
            str: Enhanced query
        """
        self.logger.info("Processing query enhancement operation")
        self.logger.debug(f"Original query: {query}")
        
        message = f"""
            Please enhance this search query while maintaining its original intent:
            {query}
            
            Provide only the enhanced query without any explanation.
            """
        
        try:
            self.logger.info("Starting query enhancement process")
            response = self._get_agent_response(
                self.agents["researcher"],
                message,
                silent=True
            )
            
            self.logger.info("Query enhancement completed")
            self.logger.debug(f"Enhanced query: {response}")
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Error during query enhancement: {str(e)}", exc_info=True)
            raise
    
    async def _analyze_chunks(self, chunks: List[Dict], query: str) -> str:
        """
        Use the analyst agent to analyze document chunks and provide insights.
        
        Args:
            chunks: List of document chunks with their metadata
            query: Original query for context
            
        Returns:
            str: Analysis of the chunks
        """
        self.logger.info("Processing chunk analysis operation")
        self.logger.debug(f"Number of chunks to analyze: {len(chunks)}")
        
        # Process chunks in batches of 3 for better performance
        BATCH_SIZE = 3
        analyses = []
        
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            self.logger.info(f"Processing batch {i//BATCH_SIZE + 1} of {(len(chunks) + BATCH_SIZE - 1)//BATCH_SIZE}")
            
            # Prepare chunks for analysis
            formatted_chunks = "\n\n".join([
                f"Chunk {j+1}:\n{chunk['content']}"
                for j, chunk in enumerate(batch)
            ])
            
            message = f"""
                Analyze these document chunks in relation to the following query:
                Query: {query}
                
                Document chunks:
                {formatted_chunks}
                
                Provide a concise analysis focusing on relevance to the query.
                """
            
            try:
                self.logger.info(f"Starting analysis of batch {i//BATCH_SIZE + 1}")
                response = self._get_agent_response(
                    self.agents["analyst"],
                    message,
                    silent=True
                )
                analyses.append(response.strip())
                
            except Exception as e:
                self.logger.error(f"Error during chunk analysis: {str(e)}", exc_info=True)
                raise
        
        # Combine all analyses
        combined_analysis = "\n\n".join(analyses)
        self.logger.info("All batch analyses completed")
        
        # Generate final summary
        summary_message = f"""
            Synthesize the following analyses into a single coherent response:
            {combined_analysis}
            
            Focus on the most relevant information to the query: {query}
        """
        
        try:
            self.logger.info("Generating final summary")
            final_summary = self._get_agent_response(
                self.agents["analyst"],
                summary_message,
                silent=True
            )
            
            self.logger.info("Chunk analysis completed")
            return final_summary.strip()
            
        except Exception as e:
            self.logger.error(f"Error during final summary: {str(e)}", exc_info=True)
            raise 