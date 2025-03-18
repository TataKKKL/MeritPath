import React, { useState, useEffect } from "react";
import Head from "next/head";
import { useRouter } from "next/router";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ArrowLeftIcon, ExternalLinkIcon } from "@radix-ui/react-icons";
import Link from "next/link";
import type { GetServerSidePropsContext } from 'next';

interface CiterPapers {
  [yourPaperTitle: string]: string[]; // Your paper title -> array of citer's papers that cited it
}

interface CiterDetail {
  citer_id: string;
  semantic_scholar_id: string;
  citer_name: string;
  paper_count: number;
  total_citations: number;
  papers: CiterPapers;
}

interface CiterDetailProps {
  citer: CiterDetail;
  user: {
    id: string;
    name: string;
  };
}

export default function CiterDetail({ citer, user }: CiterDetailProps) {
  const router = useRouter();

  if (!citer) {
    return (
      <div className="container mx-auto py-10">
        <Card>
          <CardContent className="pt-6">
            <p>Citer not found.</p>
            <Link href="/citers">
              <Button className="mt-4">
                <ArrowLeftIcon className="mr-2 h-4 w-4" /> Back to Citers
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{citer.citer_name} | MeritPath</title>
      </Head>
      
      <div className="container mx-auto py-10 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold tracking-tight">{citer.citer_name}</h1>
          <Link href="/citers">
            <Button variant="outline">
              <ArrowLeftIcon className="mr-2 h-4 w-4" /> Back to Citers
            </Button>
          </Link>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>Researcher Information</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Name</dt>
                <dd className="text-lg">
                  <a 
                    href={`https://www.semanticscholar.org/author/${citer.semantic_scholar_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:underline text-blue-600 flex items-center"
                  >
                    {citer.citer_name}
                    <ExternalLinkIcon className="ml-1 h-4 w-4" />
                  </a>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Total Papers Published</dt>
                <dd className="text-lg">{citer.paper_count}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Citations to Your Work</dt>
                <dd className="text-lg">{citer.total_citations}</dd>
              </div>
            </dl>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Citation Details</CardTitle>
            <CardDescription>Papers by {citer.citer_name} that cite your work</CardDescription>
          </CardHeader>
          <CardContent>
            {Object.entries(citer.papers).map(([yourPaper, citingPapers]) => (
              <div key={yourPaper} className="mb-8">
                <h3 className="text-lg font-semibold mb-2">Your Paper: {yourPaper}</h3>
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Citing Paper</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {citingPapers.map((paper, index) => (
                        <TableRow key={index}>
                          <TableCell>{paper}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </>
  );
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const { withServerPropsAuth, makeServerPropsAuthRequest } = require('@/utils/auth/authServerPropsHandler');
  
  return withServerPropsAuth(context, async (user, accessToken) => {
    if (!user) {
      return {
        redirect: {
          destination: '/login',
          permanent: false,
        },
      };
    }
    
    const { id } = context.params as { id: string };
    
    // Fetch citer details from the API
    let citer = null;
    try {
      citer = await makeServerPropsAuthRequest(
        context,
        `/api/users/${id}/individual_citer`
      );
      
      console.log('[getServerSideProps] Fetched individual citer data:', !!citer);
    } catch (error) {
      console.error("[getServerSideProps] Error fetching individual citer data:", error);
    }
    
    if (!citer) {
      return {
        notFound: true,
      };
    }
    
    return {
      props: {
        user,
        citer,
      },
    };
  });
} 