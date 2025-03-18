import { User } from '@supabase/supabase-js';
import { UserProfile } from './user';

/**
 * Props for the Home component
 */
export interface HomeProps {
  user: User | null;
  userProfile?: UserProfile;
} 