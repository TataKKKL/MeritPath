import React, { useState} from "react";
import Head from "next/head";
import { 
  Table, 
  TableBody, 
  TableCaption, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MagnifyingGlassIcon } from "@radix-ui/react-icons";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import Link from "next/link";
import type { GetServerSidePropsContext } from 'next';
import { withServerPropsAuth, makeServerPropsAuthRequest } from '@/utils/auth/authServerPropsHandler';
import { CiterData, CitersListProps } from "@/types/citers";
import { useCitationStore } from '@/store/citationStore';

export default function Citers({ citers}: CitersListProps) {
  const [searchText, setSearchText] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [sortConfig, setSortConfig] = useState<{
    key: keyof CiterData;
    direction: 'ascending' | 'descending';
  } | null>({ key: 'total_citations', direction: 'descending' });

  // Add this to access the store state
  const citersProcessingStatus = useCitationStore(state => state.citersProcessingStatus);

  // Filter data based on search text
  const filteredData = citers.filter(
    item =>
      item.citer_name.toLowerCase().includes(searchText.toLowerCase())
  );

  // Apply sorting to data
  const sortedData = React.useMemo(() => {
    const sortableData = [...filteredData];
    if (sortConfig !== null) {
      sortableData.sort((a, b) => {
        if (sortConfig.key === 'citer_name') {
          return sortConfig.direction === 'ascending'
            ? a.citer_name.localeCompare(b.citer_name)
            : b.citer_name.localeCompare(a.citer_name);
        }
        // For numeric fields
        return sortConfig.direction === 'ascending'
          ? (a[sortConfig.key] as number) - (b[sortConfig.key] as number)
          : (b[sortConfig.key] as number) - (a[sortConfig.key] as number);
      });
    }
    return sortableData;
  }, [filteredData, sortConfig]);

  // Sort data by a given key
  const requestSort = (key: keyof CiterData) => {
    let direction: 'ascending' | 'descending' = 'ascending';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  // Calculate pagination values
  const totalPages = Math.ceil(sortedData.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const paginatedData = sortedData.slice(startIndex, startIndex + pageSize);
  
  // Handle pagination
  const nextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };
  
  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  return (
    <>
      <Head>
        <title>Citers | MeritPath</title>
      </Head>
      
      <div className="container mx-auto py-10 space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold tracking-tight">Researchers Who Cited Your Work</h1>
        </div>
        
        {citersProcessingStatus === 'done' ? (
          <>
            <Card className="bg-green-50 border-green-200">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-2">
                  <div className="h-4 w-4 rounded-full bg-green-500"></div>
                  <p>Here&apos;s the list of your citers data.</p>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Citation Network</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-4 mb-6">
                  <div className="relative flex-1 w-full sm:max-w-sm">
                    <MagnifyingGlassIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      type="search"
                      placeholder="Search by name..."
                      className="pl-8"
                      value={searchText}
                      onChange={(e) => setSearchText(e.target.value)}
                    />
                  </div>
                </div>
                
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead 
                          className="cursor-pointer" 
                          onClick={() => requestSort('citer_name')}
                        >
                          Name {sortConfig?.key === 'citer_name' && (sortConfig.direction === 'ascending' ? '↑' : '↓')}
                        </TableHead>
                        <TableHead 
                          className="cursor-pointer text-right" 
                          onClick={() => requestSort('paper_count')}
                        >
                          Papers Published {sortConfig?.key === 'paper_count' && (sortConfig.direction === 'ascending' ? '↑' : '↓')}
                        </TableHead>
                        <TableHead 
                          className="cursor-pointer text-right" 
                          onClick={() => requestSort('total_citations')}
                        >
                          Citations to Your Work {sortConfig?.key === 'total_citations' && (sortConfig.direction === 'ascending' ? '↑' : '↓')}
                        </TableHead>
                        <TableHead className="w-[100px]">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {sortedData.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={4} className="h-24 text-center">
                            No results found.
                          </TableCell>
                        </TableRow>
                      ) : (
                        paginatedData.map((item) => (
                          <TableRow key={item.citer_id}>
                            <TableCell className="font-medium">
                              <a 
                                href={`https://www.semanticscholar.org/author/${item.semantic_scholar_id}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="hover:underline text-blue-600"
                              >
                                {item.citer_name}
                              </a>
                            </TableCell>
                            <TableCell className="text-right">{item.paper_count}</TableCell>
                            <TableCell className="text-right">{item.total_citations}</TableCell>
                            <TableCell>
                              <Link href={`/citers/${item.citer_id}`}>
                                <Button variant="outline" size="sm">View Details</Button>
                              </Link>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                    <TableCaption>
                      {sortedData.length > 0 && (
                        <div className="flex justify-between text-sm">
                          <span>Showing {Math.min(pageSize, sortedData.length - startIndex)} of {sortedData.length} entries</span>
                          <span>
                            Total Citations: {sortedData.reduce((sum, item) => sum + item.total_citations, 0)}
                          </span>
                        </div>
                      )}
                    </TableCaption>
                  </Table>
                </div>
                
                {sortedData.length > 0 && (
                  <div className="flex items-center justify-end space-x-2 py-4">
                    <div className="flex-1 text-sm text-muted-foreground">
                      Page {currentPage} of {totalPages}
                    </div>
                    <Select
                      value={String(pageSize)}
                      onValueChange={(value) => {
                        setPageSize(Number(value));
                        setCurrentPage(1);
                      }}
                    >
                      <SelectTrigger className="h-8 w-[70px]">
                        <SelectValue placeholder={pageSize} />
                      </SelectTrigger>
                      <SelectContent side="top">
                        {[5, 10, 15, 20].map((size) => (
                          <SelectItem key={size} value={String(size)}>
                            {size}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={prevPage}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={nextPage}
                      disabled={currentPage === totalPages}
                    >
                      Next
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        ) : (
          <Card className="bg-amber-50 border-amber-200">
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2">
                {citersProcessingStatus === 'processing' ? (
                  <>
                    <div className="h-4 w-4 rounded-full bg-amber-500 animate-pulse"></div>
                    <p>We&apos;re currently analyzing your citation network. This may take a few minutes.</p>
                  </>
                ) : citersProcessingStatus === 'not_started' ? (
                  <>
                    <div className="h-4 w-4 rounded-full bg-gray-500"></div>
                    <p>Citation analysis has not started yet.</p>
                  </>
                ) : (
                  <>
                    <div className="h-4 w-4 rounded-full bg-red-500"></div>
                    <p>There was an issue processing your citation data. Please try again later.</p>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
} 

// Update getServerSideProps to fetch real data
export async function getServerSideProps(context: GetServerSidePropsContext) {
  return withServerPropsAuth(context, async (user) => {
    console.log('[getServerSideProps] Auth check - User:', !!user);
    
    if (!user) {
      return {
        props: { user: null, citers: [] }
      };
    }
    
    // Fetch citers data from the API
    let citers = [];
    try {
      citers = await makeServerPropsAuthRequest(
        context,
        `/api/users/${user.id}/citers`
      );
      
      console.log('[getServerSideProps] Fetched citers data:', !!citers);
    } catch (error) {
      console.error("[getServerSideProps] Error fetching citers data:", error);
      citers = []; // Use empty array if fetch fails
    }
    
    return {
      props: {
        user,
        citers: Array.isArray(citers) ? citers : [],
      },
    };
  });
}