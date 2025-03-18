import { useState, useEffect } from 'react';
import Link from 'next/link';
import type { GetServerSidePropsContext } from 'next';
import { createClient } from '@/utils/supabase/component';
import SemanticScholarIdDialog from '@/components/dialogs/SemanticScholarIdDialog';
import { withServerPropsAuth, makeServerPropsAuthRequest } from '@/utils/auth/authServerPropsHandler';
import { makeApiAuthRequest } from '@/utils/auth/authApiHandler';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ExternalLink } from "lucide-react";
import { Paper } from '@/types/paper';
import { HomeProps } from '@/types/props';

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
  }, [user, profile, supabase.auth]);

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

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background p-8">
      <h1 className="text-4xl font-bold mb-8">Welcome to the MeritPath App</h1>
      
      {user ? (
        <div className="text-center w-full max-w-4xl">
          
          {profile?.semantic_scholar_id && (
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Your Profile</CardTitle>
                <CardDescription>Your academic information</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-lg">
                    Name: {profile.name}
                  </p>
                  <p className="text-lg">
                    Semantic Scholar ID: {profile.semantic_scholar_id}
                  </p>
                  


          {/* Citation analysis eligibility section */}
          <Card className="mt-6">
            <CardHeader className="text-center">
              <CardTitle>Citation Analysis</CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              {citersAlreadyExtracted ? (
                <Button
                  variant="outline"
                  className="mt-3"
                  asChild
                >
                  <Link href="/citers">View Analysis Results</Link>
                </Button>
              ) : (
                <Button
                  onClick={handleAnalyzeCiters}
                  disabled={isProcessingCiters}
                  size="lg"
                  variant="secondary"
                >
                  {isProcessingCiters ? "Processing..." : "Analyze My Citers"}
                </Button>
              )}
            </CardContent>
          </Card>


                  
                  {profile.papers && profile.papers.length > 0 ? (
                    <div className="mt-6">
                      <h2 className="text-2xl font-semibold mb-4">Your Papers</h2>
                      <div className="overflow-x-auto">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Title</TableHead>
                              <TableHead>Year</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {profile.papers.map((paper: Paper) => (
                              <TableRow key={paper.paperId}>
                                <TableCell>
                                  <a 
                                    href={paper.url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="flex items-center text-primary hover:underline"
                                  >
                                    {paper.title}
                                    <ExternalLink className="ml-1 h-3 w-3" />
                                  </a>
                                </TableCell>
                                <TableCell>{paper.year}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    </div>
                  ) : null}
                </div>
              </CardContent>
            </Card>
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
          <Button asChild size="lg">
            <Link href="/login">Log In</Link>
          </Button>
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