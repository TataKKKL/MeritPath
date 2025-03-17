import { useState, useEffect } from 'react';
import Link from 'next/link';
import type { User } from '@supabase/supabase-js';
import type { GetServerSidePropsContext } from 'next';
import { createClient } from '@/utils/supabase/component';
import { createClient as createServerClient } from '@/utils/supabase/server-props';
import SemanticScholarIdDialog from '@/components/dialogs/SemanticScholarIdDialog';

// Define a proper type for the user profile
interface UserProfile {
  id: string;
  semantic_scholar_id?: string;
  name?: string;
  email?: string;
  influential_citation_count?: number;
  author_paper_count?: number;
  papers?: string[]; // Changed from any[] to string[]
  created_at?: string;
}

interface HomeProps {
  user: User | null;
  userProfile?: UserProfile;
}

const Home = ({ user, userProfile }: HomeProps) => {
  const [showDialog, setShowDialog] = useState(false);
  const [profile, setProfile] = useState(userProfile);
  const supabase = createClient();

  useEffect(() => {
    // If user is logged in and has no semantic_scholar_id, show the dialog
    if (user && profile && !profile.semantic_scholar_id) {
      setShowDialog(true);
    }
  }, [user, profile]);

  const handleSuccess = async () => {
    // Refresh the profile data after updating
    if (user) {
      const { data, error } = await supabase
        .from("users")
        .select("*")
        .eq("id", user.id)
        .single();
      
      if (!error && data) {
        setProfile(data);
      }
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-gray-900 p-8">
      <h1 className="text-black dark:text-white text-4xl mb-8">Welcome to the MeritPath App</h1>
      
      {user ? (
        <div className="text-center">
          <p className="text-black dark:text-white text-xl mb-4">
            Logged in as: {user.email}
          </p>
          
          {profile?.semantic_scholar_id && (
            <p className="text-black dark:text-white text-lg mb-4">
              Semantic Scholar ID: {profile.semantic_scholar_id}
            </p>
          )}
          
          {/* Dialog to set Semantic Scholar ID */}
          <SemanticScholarIdDialog 
            open={showDialog} 
            onOpenChange={setShowDialog} 
            onSuccess={handleSuccess}
            userId={user.id}
          />
        </div>
      ) : (
        <div className="text-center">
          <Link 
            href="/login" 
            className="inline-block px-6 py-3 text-white bg-blue-600 rounded hover:bg-blue-700 transition-colors"
          >
            Log In
          </Link>
        </div>
      )}
    </div>
  );
};

export default Home;

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const supabase = createServerClient(context);
  const { data: { user }, error } = await supabase.auth.getUser();
  
  if (error) {
    console.error('Error fetching user:', error);
    return {
      props: {
        user: null,
        error: error.message,
      },
    };
  }
  
  // If user is logged in, fetch their profile from the users table
  let userProfile = null;
  if (user) {
    const { data, error: profileError } = await supabase
      .from("users")
      .select("*")
      .eq("id", user.id)
      .single();
    
    if (profileError) {
      console.error("Error fetching user profile:", profileError);
    } else {
      userProfile = data;
    }
  }
  
  return {
    props: {
      user: user || null,
      userProfile,
    },
  };
}