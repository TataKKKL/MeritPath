import { useState, useEffect } from 'react';
import Link from 'next/link';
import type { User } from '@supabase/supabase-js';
import type { GetServerSidePropsContext } from 'next';
import { createClient } from '@/utils/supabase/component';
import SemanticScholarIdDialog from '@/components/dialogs/SemanticScholarIdDialog';
import { withServerPropsAuth, makeServerPropsAuthRequest } from '@/utils/auth/authServerPropsHandler';
import { makeApiAuthRequest } from '@/utils/auth/authApiHandler';


// Define a Paper type
interface Paper {
  url: string;
  year: number;
  title: string;
  paperId: string;
}

// Define a proper type for the user profile
interface UserProfile {
  id: string;
  semantic_scholar_id?: string;
  name?: string;
  email?: string;
  influential_citation_count?: number;
  author_paper_count?: number;
  papers?: Paper[];
  created_at?: string;
}

interface HomeProps {
  user: User | null;
  userProfile?: UserProfile;
}

const Home = ({ user, userProfile }: HomeProps) => {
  const [showDialog, setShowDialog] = useState(false);
  const [profile, setProfile] = useState(userProfile);
  const [isProcessingCiters, setIsProcessingCiters] = useState(false);
  const [citersAlreadyExtracted, setCitersAlreadyExtracted] = useState(false);
  const supabase = createClient();

  useEffect(() => {
    // If user is logged in and has no semantic_scholar_id, show the dialog
    if (user && profile && !profile.semantic_scholar_id) {
      setShowDialog(true);
    }
  }, [user, profile]);

  useEffect(() => {
    // Check if citers have already been extracted when user and profile are available
    const checkCitersExtracted = async () => {
      if (user && profile?.semantic_scholar_id) {
        try {
          const { data: { session } } = await supabase.auth.getSession();
          
          if (session?.access_token) {
            const response = await makeApiAuthRequest(
              session.access_token,
              `/api/users/${user.id}/job_done`,
              { method: 'GET' }
            );
            
            if (response && response.job_done) {
              setCitersAlreadyExtracted(true);
            }
          }
        } catch (error) {
          console.error('Error checking if citers were extracted:', error);
        }
      }
    };
    
    checkCitersExtracted();
  }, [user, profile]);

  const handleSuccess = async () => {
    // Refresh the profile data after updating using the API
    if (user) {
      try {
        // Get the session which contains the access token
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session?.access_token) {
          // Use makeApiAuthRequest with the session access token
          try {
            const data = await makeApiAuthRequest(
              session.access_token,
              `/api/users/${user.id}`,
              { method: 'GET' }
            );
            
            setProfile(data);
            console.log('Profile updated successfully:', data);
          } catch (error) {
            console.error('Error fetching updated profile:', error);
          }
        }
      } catch (error) {
        console.error('Error fetching updated profile:', error);
      }
    }
  };

  const handleAnalyzeCiters = async () => {
    if (!user) return;
    
    setIsProcessingCiters(true);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (session?.access_token) {
        await makeApiAuthRequest(
          session.access_token,
          "/api/sqs/jobs",
          {
            method: 'POST',
            body: JSON.stringify({
              job_type: "find_citers",
              job_params: {
                user_id: user.id
              }
            })
          }
        );
        
        alert("Your citation analysis has been started. Results will be available soon.");
      }
    } catch (error) {
      console.error('Error starting citation analysis:', error);
      alert("Failed to start citation analysis. Please try again later.");
    } finally {
      setIsProcessingCiters(false);
    }
  };

  // Check if user is eligible for citation analysis
  const isEligibleForCitationAnalysis = profile && 
    (profile.influential_citation_count || 0) < 5 && 
    (profile.author_paper_count || 0) < 10;

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-gray-900 p-8">
      <h1 className="text-black dark:text-white text-4xl mb-8">Welcome to the MeritPath App</h1>
      
      {user ? (
        <div className="text-center">
          {/* <p className="text-black dark:text-white text-xl mb-4">
            Logged in as: {user.email}
          </p> */}
          
          {profile?.semantic_scholar_id && (
            <div className="mb-8">
              <p className="text-black dark:text-white text-lg mb-4">
                Name: {profile.name}
              </p>
              <p className="text-black dark:text-white text-lg mb-4">
                Semantic Scholar ID: {profile.semantic_scholar_id}
              </p>
              
              {/* Citation analysis eligibility section */}
              <div className="mt-6 mb-6 p-4 border rounded bg-gray-50 dark:bg-gray-800">
                {isEligibleForCitationAnalysis ? (
                  <div>
                    <p className="text-green-600 dark:text-green-400 font-medium mb-3">
                      Congratulations, you are eligible for analyzing your citers!
                    </p>
                    {citersAlreadyExtracted ? (
                      <p className="text-blue-600 dark:text-blue-400">
                        Your citers have already been extracted and analyzed.
                      </p>
                    ) : (
                      <button
                        onClick={handleAnalyzeCiters}
                        disabled={isProcessingCiters}
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isProcessingCiters ? "Processing..." : "Analyze My Citers"}
                      </button>
                    )}
                  </div>
                ) : (
                  <p className="text-amber-600 dark:text-amber-400">
                    Sorry, our analyzing citers feature is only available to junior researchers.
                  </p>
                )}
              </div>
              
              {profile.papers && profile.papers.length > 0 && (
                <div className="mt-6">
                  <h2 className="text-black dark:text-white text-2xl mb-4">Your Papers</h2>
                  <div className="overflow-x-auto">
                    <table className="min-w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700">
                      <thead>
                        <tr className="bg-gray-100 dark:bg-gray-700">
                          <th className="py-2 px-4 border-b text-left text-black dark:text-white">Title</th>
                          <th className="py-2 px-4 border-b text-left text-black dark:text-white">Year</th>
                        </tr>
                      </thead>
                      <tbody>
                        {profile.papers.map((paper: Paper, index: number) => (
                          <tr key={paper.paperId} className={index % 2 === 0 ? 'bg-gray-50 dark:bg-gray-800' : 'bg-white dark:bg-gray-900'}>
                            <td className="py-2 px-4 border-b text-black dark:text-white">
                              <a 
                                href={paper.url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-blue-600 dark:text-blue-400 hover:underline"
                              >
                                {paper.title}
                              </a>
                            </td>
                            <td className="py-2 px-4 border-b text-black dark:text-white">{paper.year}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
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
  return withServerPropsAuth(context, async (user, accessToken) => {
    console.log('[getServerSideProps] Auth check - User:', !!user);
    console.log('[getServerSideProps] Auth check - Token:', !!accessToken);

    // If user is logged in, fetch their profile from the API
    let userProfile = null;
    if (user) {
      try {
        // Use the auth request helper to fetch user profile
        userProfile = await makeServerPropsAuthRequest(
          context,
          `/api/users/${user.id}`
        );
        
        console.log('[getServerSideProps] Fetched user profile:', !!userProfile);
      } catch (error) {
        console.error("[getServerSideProps] Error fetching user profile:", error);
      }
    }
    
    return {
      props: {
        user,
        userProfile,
      },
    };
  });
}