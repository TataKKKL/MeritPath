import { Paper } from './paper';

/**
 * Represents a user profile with academic information
 */
export interface UserProfile {
  id: string;
  semantic_scholar_id?: string;
  name?: string;
  email?: string;
  influential_citation_count?: number;
  author_paper_count?: number;
  papers?: Paper[];
  created_at?: string;
} 