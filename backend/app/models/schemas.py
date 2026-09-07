from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# ================= AUTH SCHEMAS =================
class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ================= REPOSITORY SCHEMAS =================
class RepositoryCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class RepositoryResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    created_at: str
    document_count: Optional[int] = 0

# ================= DOCUMENT SCHEMAS =================
class MetadataResponse(BaseModel):
    category: str
    category_confidence: float
    executive_summary: str
    extracted_entities: Dict[str, Any]
    token_count: int
    word_count: int
    processed_at: str

class DocumentResponse(BaseModel):
    id: int
    repository_id: int
    original_filename: str
    file_extension: str
    file_size_bytes: int
    mime_type: str
    processing_status: str
    created_at: str
    category: Optional[str] = None
    summary: Optional[str] = None

class DocumentDetailResponse(DocumentResponse):
    raw_text: Optional[str] = None
    metadata: Optional[MetadataResponse] = None

# ================= SEARCH & RAG SCHEMAS =================
class RagQueryRequest(BaseModel):
    query: str
    repository_id: Optional[int] = None
    document_id: Optional[int] = None

class RagSource(BaseModel):
    document_id: int
    document_name: str
    category: str
    chunk_index: int
    relevance_score: float
    excerpt: str

class RagQueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[RagSource]
    model_used: str

class SearchResultItem(BaseModel):
    document_id: int
    document_name: str
    category: str
    snippet: str
    relevance: float

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]

# ================= DASHBOARD SCHEMAS =================
class CategoryDistribution(BaseModel):
    category: str
    count: int
    percentage: float

class FormatDistribution(BaseModel):
    extension: str
    count: int

class DashboardStatsResponse(BaseModel):
    total_documents: int
    total_repositories: int
    total_storage_bytes: int
    status_counts: Dict[str, int]
    categories: List[CategoryDistribution]
    formats: List[FormatDistribution]

class AuditLogItem(BaseModel):
    id: int
    action: str
    status: str
    details: Optional[str]
    timestamp: str

# ================= NOTEBOOKLM STUDIO SCHEMAS =================
class NotebookSourceItem(BaseModel):
    id: int
    original_filename: str
    category: str
    file_extension: str
    word_count: int
    summary_snippet: str

class NotebookQueryRequest(BaseModel):
    document_ids: List[int]
    query: str
    mode: Optional[str] = "chat"

class NotebookCitation(BaseModel):
    citation_id: int
    document_id: int
    document_name: str
    quote: str

class NotebookResponse(BaseModel):
    query: str
    mode: str
    answer: str
    citations: List[NotebookCitation]
    sources_used: List[str]
    model_used: str
    total_words_analyzed: int
