// Define interfaces for citer data
export interface CiterData {
  citer_id: string;
  semantic_scholar_id: string;
  citer_name: string;
  paper_count: number;
  total_citations: number;
}

// Interface for citer papers (used in detail view)
export interface CiterPapers {
  [yourPaperTitle: string]: string[]; // Your paper title -> array of citer's papers that cited it
}

// Extended interface for citer detail page
export interface CiterDetail extends CiterData {
  papers: CiterPapers;
}

// User interface for type safety
export interface User {
  id: string;
  name: string;
  // Add other user properties as needed
}

// Props type for the citers list component
export interface CitersListProps {
  user: User;
  citers: CiterData[];
}

// Props type for the citer detail component
export interface CiterDetailProps {
  citer: CiterDetail;
  user: User;
} 