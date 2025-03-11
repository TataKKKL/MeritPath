import React, { useState, useEffect } from "react";
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
import { ReloadIcon, MagnifyingGlassIcon } from "@radix-ui/react-icons";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface CitationData {
  key: string;
  rank: number;
  citingAuthor: string;
  authorId: string;
  totalCitations: number;
  paperCount: number;
  citedPapers: string;
}

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<CitationData[]>([]);
  const [searchText, setSearchText] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Generate mock data
  useEffect(() => {
    const mockData: CitationData[] = Array.from({ length: 50 }, (_, i) => ({
      key: `${i}`,
      rank: i + 1,
      citingAuthor: `Dr. ${['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'][i % 5]} ${['A', 'B', 'C', 'D', 'E'][Math.floor(i / 10)]}`,
      authorId: `A${100000 + i}`,
      totalCitations: Math.floor(Math.random() * 5000) + 100,
      paperCount: Math.floor(Math.random() * 200) + 10,
      citedPapers: `Paper ${i % 5 + 1} → Citing Paper ${i % 7 + 1}`,
    }));

    setTimeout(() => {
      setData(mockData);
      setLoading(false);
    }, 1000);
  }, []);

  // Filter data based on search text
  const filteredData = data.filter(
    item =>
      item.citingAuthor.toLowerCase().includes(searchText.toLowerCase()) ||
      item.authorId.toLowerCase().includes(searchText.toLowerCase()) ||
      item.citedPapers.toLowerCase().includes(searchText.toLowerCase())
  );

  // Sort data by a given key
  const sortData = (key: keyof CitationData, ascending: boolean) => {
    const sortedData = [...data].sort((a, b) => {
      if (typeof a[key] === 'string') {
        return ascending 
          ? (a[key] as string).localeCompare(b[key] as string) 
          : (b[key] as string).localeCompare(a[key] as string);
      }
      return ascending 
        ? (a[key] as number) - (b[key] as number) 
        : (b[key] as number) - (a[key] as number);
    });
    
    setData(sortedData);
  };

  // Calculate pagination values
  const totalPages = Math.ceil(filteredData.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const paginatedData = filteredData.slice(startIndex, startIndex + pageSize);
  
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
        <title>Citation Dashboard</title>
      </Head>
      
      <div className="container mx-auto py-10 space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Citation Dashboard</h1>
        
        <Card>
          <CardHeader>
            <CardTitle>Citation Data</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4 mb-6">
              <div className="relative flex-1 max-w-sm">
                <MagnifyingGlassIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Search authors, IDs, or papers..."
                  className="pl-8"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                />
              </div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  setLoading(true);
                  setTimeout(() => setLoading(false), 500);
                }}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
                    Loading
                  </>
                ) : (
                  <>
                    <ReloadIcon className="mr-2 h-4 w-4" />
                    Refresh
                  </>
                )}
              </Button>
            </div>
            
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[80px] cursor-pointer" onClick={() => sortData('rank', true)}>Rank</TableHead>
                    <TableHead className="cursor-pointer" onClick={() => sortData('citingAuthor', true)}>Citing Author</TableHead>
                    <TableHead>Author ID</TableHead>
                    <TableHead className="cursor-pointer" onClick={() => sortData('totalCitations', false)}>Total Citations</TableHead>
                    <TableHead className="cursor-pointer" onClick={() => sortData('paperCount', false)}>Author Paper Count</TableHead>
                    <TableHead className="max-w-[200px]">Cited Papers and Citing Papers</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={6} className="h-24 text-center">
                        Loading data...
                      </TableCell>
                    </TableRow>
                  ) : filteredData.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="h-24 text-center">
                        No results found.
                      </TableCell>
                    </TableRow>
                  ) : (
                    paginatedData.map((item) => (
                      <TableRow key={item.key}>
                        <TableCell className="font-medium">{item.rank}</TableCell>
                        <TableCell>{item.citingAuthor}</TableCell>
                        <TableCell>{item.authorId}</TableCell>
                        <TableCell>{item.totalCitations}</TableCell>
                        <TableCell>{item.paperCount}</TableCell>
                        <TableCell className="truncate max-w-[200px]" title={item.citedPapers}>
                          {item.citedPapers}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
                <TableCaption>
                  {!loading && filteredData.length > 0 && (
                    <div className="flex justify-between text-sm">
                      <span>Showing {Math.min(pageSize, filteredData.length - startIndex)} of {filteredData.length} entries</span>
                      <span>
                        Total Citations: {filteredData.reduce((sum, item) => sum + item.totalCitations, 0)} | 
                        Total Papers: {filteredData.reduce((sum, item) => sum + item.paperCount, 0)}
                      </span>
                    </div>
                  )}
                </TableCaption>
              </Table>
            </div>
            
            {/* Updated pagination */}
            {filteredData.length > 0 && (
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
                    {[10, 20, 30, 50].map((size) => (
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
                  disabled={currentPage === 1 || loading}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={nextPage}
                  disabled={currentPage === totalPages || loading}
                >
                  Next
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </>
  );
}