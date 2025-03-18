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
import { useCitationStore } from '@/store/citationStore';

const Home = ({ user, userProfile }: HomeProps) => {
  const [showDialog, setShowDialog] = useState(false);
  const [profile, setProfile] = useState(userProfile);
  const supabase = createClient();
  
  // Use the Zustand store instead of local state
  const { 
    citersProcessingStatus, 
    isEligibleForCitationAnalysis,
    setCitersProcessingStatus,
    setIsEligibleForCitationAnalysis,
    checkCitersStatus
  } = useCitationStore();

  useEffect(() => {
    // If user is logged in and has no semantic_scholar_id, show the dialog
    if (user && profile && !profile.semantic_scholar_id) {
      setShowDialog(true);
    }
  }, [user, profile]);

  console.log(profile);
  console.log('isEligibleForCitationAnalysis: ', isEligibleForCitationAnalysis);

  useEffect(() => {
    // Check if user is eligible for citation analysis
    if (profile && profile.author_paper_count && profile.author_paper_count < 10) {
      setIsEligibleForCitationAnalysis(true);
    }
  }, [profile, setIsEligibleForCitationAnalysis]);

  // Track processing status with subscription
  useEffect(() => {
    // Only setup subscription if we have a user profile
    if (!profile || !profile.id) return;
    
    console.log('Setting up Supabase subscription for user:', profile.id);
    
    // Keep track of job statuses
    const jobStatuses = new Map();
    
    // Subscribe to changes in the jobs table for this user
    const subscription = supabase
      .channel('job-status-changes')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'jobs',
          filter: `user_id=eq.${profile.id}`,
        },
        (payload) => {
          // Log all payloads to verify subscription is working
          console.log('Received payload from Supabase:', payload);
          
          // Only interested in find_citers jobs
          if (payload.new.job_type === 'find_citers') {
            console.log('Found find_citers job update:', {
              oldStatus: payload.old.status,
              newStatus: payload.new.status,
              jobId: payload.new.id
            });
            
            const jobId = payload.new.id;
            const newStatus = payload.new.status;
            
            // If a job has changed to success or failed
            if (newStatus === 'success' || newStatus === 'failed') {
              console.log('Job completed with status:', newStatus);
              setCitersProcessingStatus('done');
            }
            
            // Store the current status for future reference
            jobStatuses.set(jobId, newStatus);
          }
        }
      )
      .subscribe((status) => {
        console.log('Subscription status:', status);
      });
    
    // Clean up subscription when component unmounts
    return () => {
      console.log('Cleaning up Supabase subscription');
      subscription.unsubscribe();
    };
  }, [profile, supabase, setCitersProcessingStatus]);

  useEffect(() => {
    // Check if citers have already been extracted when user and profile are available
    if (user && profile?.semantic_scholar_id) {
      checkCitersStatus(user.id);
    }
  }, [user, profile, checkCitersStatus]);

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
    
    setCitersProcessingStatus('processing');
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
      setCitersProcessingStatus('not_started');
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
          <Card className={
            citersProcessingStatus === 'done' 
              ? "mt-6 bg-green-50 border-green-200" 
              : citersProcessingStatus === 'processing'
                ? "mt-6 bg-amber-50 border-amber-200"
                : "mt-6"
          }>
            <CardHeader className="text-center">
              <CardTitle>Citation Analysis</CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              {citersProcessingStatus === 'done' ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-center space-x-2 mb-4">
                    <div className="h-4 w-4 rounded-full bg-green-500"></div>
                    <p className="text-green-700">
                      Your citation analysis is complete!
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    className="mt-3"
                    asChild
                  >
                    <Link href="/citers">View Analysis Results</Link>
                  </Button>
                </div>
              ) : isEligibleForCitationAnalysis ? (
                citersProcessingStatus === 'processing' ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-center space-x-2 mb-4">
                      <div className="h-4 w-4 rounded-full bg-amber-500 animate-pulse"></div>
                      <p className="text-amber-700">
                        We&apos;re currently analyzing your citation network. This may take a few minutes.
                      </p>
                    </div>
                    <Button
                      disabled={true}
                      size="lg"
                      variant="secondary"
                    >
                      Processing...
                    </Button>
                  </div>
                ) : (
                  <Button
                    onClick={handleAnalyzeCiters}
                    size="lg"
                    variant="secondary"
                  >
                    Analyze My Citers
                  </Button>
                )
              ) : (
                <Button
                  variant="outline"
                  className="mt-3"
                  disabled={true}
                >
                  <span className="text-sm">You are not eligible for citation analysis</span>
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