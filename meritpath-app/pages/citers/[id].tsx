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
import { ArrowLeftIcon, ReloadIcon } from "@radix-ui/react-icons";
import Link from "next/link";

interface CiterData {
  id: string;
  name: string;
  university: string;
  totalCitations: number;
}

interface JobData {
  job_id: string;
  job_type: string;
  status: string;
  created_at: string;
  result?: {
    count?: number;
    status?: string;
    numbers?: number[];
    [key: string]: unknown;
  };
}

// Sample data for the citers table
const sampleCiters: CiterData[] = [
    { id: "1", name: "Dr. Sarah Johnson", university: "Stanford University", totalCitations: 342 },
    { id: "2", name: "Prof. Michael Chen", university: "MIT", totalCitations: 287 },
    { id: "3", name: "Dr. Emily Rodriguez", university: "University of California, Berkeley", totalCitations: 215 },
    { id: "4", name: "Prof. David Kim", university: "Harvard University", totalCitations: 198 },
    { id: "5", name: "Dr. Lisa Wang", university: "University of Oxford", totalCitations: 176 },
    { id: "6", name: "Prof. James Wilson", university: "ETH Zurich", totalCitations: 163 },
    { id: "7", name: "Dr. Sophia Patel", university: "University of Cambridge", totalCitations: 154 },
    { id: "8", name: "Prof. Robert Garcia", university: "University of Tokyo", totalCitations: 142 },
    { id: "9", name: "Dr. Olivia Martinez", university: "National University of Singapore", totalCitations: 137 },
    { id: "10", name: "Prof. Thomas Lee", university: "University of Toronto", totalCitations: 129 },
    { id: "11", name: "Dr. Emma Brown", university: "Imperial College London", totalCitations: 118 },
    { id: "12", name: "Prof. Daniel Smith", university: "Tsinghua University", totalCitations: 112 },
    { id: "13", name: "Dr. Ava Williams", university: "University of Michigan", totalCitations: 105 },
    { id: "14", name: "Prof. Alexander Davis", university: "Technical University of Munich", totalCitations: 98 },
    { id: "15", name: "Dr. Natalie Taylor", university: "University of Edinburgh", totalCitations: 92 },
  ];

export default function CiterDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [citer, setCiter] = useState<CiterData | null>(null);
  const [jobs, setJobs] = useState<JobData[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch citer details and jobs
  useEffect(() => {
    if (id) {
      // In a real app, fetch from API
      // Find citer by matching the id string with the id property in the array
      const foundCiter = sampleCiters.find(citer => citer.id === id);
      setCiter(foundCiter || null);
      
      // Fetch jobs for this citer
      fetchJobs();
    }
  }, [id]);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      // Mock data for now
      const mockJobs: JobData[] = [
        {
          job_id: "1",
          job_type: "process_citer",
          status: "completed",
          created_at: "2023-05-15T10:30:00Z",
          result: { count: 10, status: "success", numbers: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] }
        },
        {
          job_id: "2",
          job_type: "process_citer",
          status: "pending",
          created_at: "2023-05-14T14:20:00Z"
        }
      ];
      
      setJobs(mockJobs);
    } catch (error) {
      console.error("Error fetching jobs:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!citer && !loading) {
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
        <title>{citer?.name || 'Citer Detail'} | MeritPath</title>
      </Head>
      
      <div className="container mx-auto py-10 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold tracking-tight">{citer?.name || 'Loading...'}</h1>
          <Link href="/citers">
            <Button variant="outline">
              <ArrowLeftIcon className="mr-2 h-4 w-4" /> Back to Citers
            </Button>
          </Link>
        </div>
        
        {citer && (
          <Card>
            <CardHeader>
              <CardTitle>Citer Information</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Name</dt>
                  <dd className="text-lg">{citer.name}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">University</dt>
                  <dd className="text-lg">{citer.university}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Total Citations</dt>
                  <dd className="text-lg">{citer.totalCitations}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>
        )}
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Processing Jobs</CardTitle>
              <CardDescription>Jobs related to this citer</CardDescription>
            </div>
            <Button 
              variant="destructive"
              onClick={(e) => {
                e.preventDefault();
                // Do nothing when clicked
                console.log("Button clicked, but no action taken");
              }}
            >
              Start New Job
            </Button>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Job ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created At</TableHead>
                    <TableHead>Result</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={5} className="h-24 text-center">
                        <ReloadIcon className="h-5 w-5 animate-spin mx-auto" />
                      </TableCell>
                    </TableRow>
                  ) : jobs.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="h-24 text-center">
                        No jobs found for this citer.
                      </TableCell>
                    </TableRow>
                  ) : (
                    jobs.map((job) => (
                      <TableRow key={job.job_id}>
                        <TableCell className="font-mono text-xs">{job.job_id}</TableCell>
                        <TableCell>{job.job_type}</TableCell>
                        <TableCell>
                          <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                            job.status === 'pending' ? 'bg-blue-100 text-blue-800' :
                            job.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                            job.status === 'completed' ? 'bg-green-100 text-green-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                          </span>
                        </TableCell>
                        <TableCell>{new Date(job.created_at).toLocaleString()}</TableCell>
                        <TableCell>
                          {job.result ? (
                            <details>
                              <summary className="cursor-pointer">View Result</summary>
                              <pre className="mt-2 p-2 bg-muted rounded text-xs overflow-auto">
                                {JSON.stringify(job.result, null, 2)}
                              </pre>
                            </details>
                          ) : (
                            <span className="text-muted-foreground">No result yet</span>
                          )}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
} 