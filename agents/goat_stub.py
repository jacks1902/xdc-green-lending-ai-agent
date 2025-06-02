# goat_stub.py

class BaseGOATAgent:
    def analyze_and_execute(self, borrower_data=None, project_data=None, rwa_data=None, context=None):
        """
        This is the base class for a GOAT SDK-compatible agent.
        Any subclass (e.g., GOATAgent) must override this method.

        Parameters:
        - borrower_data (pd.DataFrame or dict): Information about the borrower.
        - project_data (pd.DataFrame or dict): Details about the project.
        - rwa_data (pd.DataFrame or dict): Real World Asset details.
        - context (dict): Optional metadata, environmental data, or risk assumptions.

        Returns:
        - dict: Recommendation output including risk level, decision, justification, etc.
        """
        raise NotImplementedError("This method should be implemented by a subclass.")
