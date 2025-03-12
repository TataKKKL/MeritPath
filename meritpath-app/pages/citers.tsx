import React, { useState } from "react";
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
import { MagnifyingGlassIcon} from "@radix-ui/react-icons";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface CiterData {
  id: string;
  name: string;
  status: "not started" | "pending" | "finished" ;
  university: string;
  totalCitations: number;
}

// Sample data for the citers table
const sampleCiters: CiterData[] = [
  { id: "1", name: "Dr. Sarah Johnson", status: "not started", university: "Stanford University", totalCitations: 342 },
  { id: "2", name: "Prof. Michael Chen", status: "not started", university: "MIT", totalCitations: 287 },
  { id: "3", name: "Dr. Emily Rodriguez", status: "not started", university: "University of California, Berkeley", totalCitations: 215 },
  { id: "4", name: "Prof. David Kim", status: "not started", university: "Harvard University", totalCitations: 198 },
  { id: "5", name: "Dr. Lisa Wang", status: "not started", university: "University of Oxford", totalCitations: 176 },
  { id: "6", name: "Prof. James Wilson", status: "not started", university: "ETH Zurich", totalCitations: 163 },
  { id: "7", name: "Dr. Sophia Patel", status: "not started", university: "University of Cambridge", totalCitations: 154 },
  { id: "8", name: "Prof. Robert Garcia", status: "not started", university: "University of Tokyo", totalCitations: 142 },
  { id: "9", name: "Dr. Olivia Martinez", status: "not started", university: "National University of Singapore", totalCitations: 137 },
  { id: "10", name: "Prof. Thomas Lee", status: "not started", university: "University of Toronto", totalCitations: 129 },
  { id: "11", name: "Dr. Emma Brown", status: "not started", university: "Imperial College London", totalCitations: 118 },
  { id: "12", name: "Prof. Daniel Smith", status: "not started", university: "Tsinghua University", totalCitations: 112 },
  { id: "13", name: "Dr. Ava Williams", status: "not started", university: "University of Michigan", totalCitations: 105 },
  { id: "14", name: "Prof. Alexander Davis", status: "not started", university: "Technical University of Munich", totalCitations: 98 },
  { id: "15", name: "Dr. Natalie Taylor", status: "not started", university: "University of Edinburgh", totalCitations: 92 },
];

export default function Citers() {
  const [searchText, setSearchText] = useState("");
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [sortConfig, setSortConfig] = useState<{
    key: keyof CiterData;
    direction: 'ascending' | 'descending';
  } | null>({ key: 'totalCitations', direction: 'descending' });

  // Filter data based on search text and status
  const filteredData = sampleCiters.filter(
    item =>
      (item.name.toLowerCase().includes(searchText.toLowerCase()) ||
       item.university.toLowerCase().includes(searchText.toLowerCase())) &&
      (!statusFilter || item.status === statusFilter)
  );

  // Apply sorting to data
  const sortedData = React.useMemo(() => {
    const sortableData = [...filteredData];
    if (sortConfig !== null) {
      sortableData.sort((a, b) => {
        if (typeof a[sortConfig.key] === 'string') {
          return sortConfig.direction === 'ascending'
            ? (a[sortConfig.key] as string).localeCompare(b[sortConfig.key] as string)
            : (b[sortConfig.key] as string).localeCompare(a[sortConfig.key] as string);
        }
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
        <h1 className="text-3xl font-bold tracking-tight">Citers Management</h1>
        
        <Card>
          <CardHeader>
            <CardTitle>Potential Recommenders</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-4 mb-6">
              <div className="relative flex-1 w-full sm:max-w-sm">
                <MagnifyingGlassIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Search by name or university..."
                  className="pl-8"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                />
              </div>
              
              <Select
                value={statusFilter || "all"}
                onValueChange={(value) => setStatusFilter(value === "all" ? null : value)}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All statuses</SelectItem>
                  <SelectItem value="not started">Not Started</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="finished">Finished</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead 
                      className="cursor-pointer" 
                      onClick={() => requestSort('name')}
                    >
                      Name {sortConfig?.key === 'name' && (sortConfig.direction === 'ascending' ? '↑' : '↓')}
                    </TableHead>
                    <TableHead 
                      className="cursor-pointer" 
                      onClick={() => requestSort('status')}
                    >
                      Status {sortConfig?.key === 'status' && (sortConfig.direction === 'ascending' ? '↑' : '↓')}
                    </TableHead>
                    <TableHead 
                      className="cursor-pointer" 
                      onClick={() => requestSort('university')}
                    >
                      University {sortConfig?.key === 'university' && (sortConfig.direction === 'ascending' ? '↑' : '↓')}
                    </TableHead>
                    <TableHead 
                      className="cursor-pointer text-right" 
                      onClick={() => requestSort('totalCitations')}
                    >
                      Total Citations {sortConfig?.key === 'totalCitations' && (sortConfig.direction === 'ascending' ? '↑' : '↓')}
                    </TableHead>
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
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{item.name}</TableCell>
                        <TableCell>
                          <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                            item.status === 'not started' ? 'bg-gray-100 text-gray-800' :
                            item.status === 'pending' ? 'bg-blue-100 text-blue-800' :
                            item.status === 'finished' ? 'bg-green-100 text-green-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                          </span>
                        </TableCell>
                        <TableCell>{item.university}</TableCell>
                        <TableCell className="text-right">{item.totalCitations}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
                <TableCaption>
                  {sortedData.length > 0 && (
                    <div className="flex justify-between text-sm">
                      <span>Showing {Math.min(pageSize, sortedData.length - startIndex)} of {sortedData.length} entries</span>
                      <span>
                        Total Citations: {sortedData.reduce((sum, item) => sum + item.totalCitations, 0)}
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
      </div>
    </>
  );
} 