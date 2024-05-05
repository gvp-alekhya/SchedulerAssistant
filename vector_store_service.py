
class VectorStoreService:
    def __init__(self, client):
        self.client = client
        # Create a vector store caled "Financial Statements"
        self.store =  self.client.beta.vector_stores.create(name="Financial Statements")
    
    def get_store_id(self):
        return self.store
    
    def loadfile(self, file_paths):
        
        # Ready the files for upload to OpenAI 
        file_streams = [open(path, "rb") for path in file_paths]
        
        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id= self.store.id, files=file_streams
        )
        
        # You can print the status and the file counts of the batch to see the result of this operation. 
        print(file_batch.status)
        print(file_batch.file_counts)

    