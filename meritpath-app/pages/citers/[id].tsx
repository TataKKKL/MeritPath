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
  titles?: string[];
  recentPapers?: {
    id: string;
    title: string;
    journal: string;
    year: number;
    citations: number;
  }[];
  mutualConnections?: {
    id: string;
    name: string;
    university: string;
    relationship: string;
  }[];
}

// Sample data for the citers table
const sampleCiters: CiterData[] = [
    { 
      id: "1", 
      name: "Dr. Sarah Johnson", 
      university: "Stanford University", 
      totalCitations: 342,
      titles: ["ACM Fellow", "IEEE Senior Member", "Associate Professor"],
      recentPapers: [
        { id: "p1", title: "Advances in Neural Network Architectures", journal: "Journal of Machine Learning", year: 2023, citations: 45 },
        { id: "p2", title: "Transformer Models for Natural Language Processing", journal: "Computational Linguistics", year: 2022, citations: 78 },
        { id: "p3", title: "Ethical Considerations in AI Development", journal: "AI Ethics", year: 2022, citations: 32 },
      ],
      mutualConnections: [
        { id: "m1", name: "Dr. James Wilson", university: "Stanford University", relationship: "Co-author on 3 papers" },
        { id: "m2", name: "Prof. Emily Chen", university: "MIT", relationship: "Research collaborator" },
      ]
    },
    { 
      id: "2", 
      name: "Prof. Michael Chen", 
      university: "MIT", 
      totalCitations: 287,
      titles: ["IEEE Fellow", "AAAI Member", "Full Professor"],
      recentPapers: [
        { id: "p4", title: "Reinforcement Learning in Robotics", journal: "Robotics and Automation", year: 2023, citations: 38 },
        { id: "p5", title: "Deep Learning for Computer Vision", journal: "IEEE Transactions on Pattern Analysis", year: 2022, citations: 65 },
        { id: "p6", title: "Autonomous Systems Design", journal: "Journal of Autonomous Systems", year: 2021, citations: 42 },
      ],
      mutualConnections: [
        { id: "m3", name: "Dr. Lisa Wang", university: "University of Oxford", relationship: "PhD Advisor" },
        { id: "m4", name: "Prof. Robert Garcia", university: "University of Tokyo", relationship: "Conference committee member" },
      ]
    },
    { 
      id: "3", 
      name: "Dr. Emily Rodriguez", 
      university: "University of California, Berkeley", 
      totalCitations: 215,
      titles: ["NSF CAREER Award", "Assistant Professor", "Google Research Fellow"],
      recentPapers: [
        { id: "p7", title: "Quantum Computing Applications in ML", journal: "Quantum Information Processing", year: 2023, citations: 29 },
        { id: "p8", title: "Sustainable AI: Energy Efficiency in Large Models", journal: "Nature Computational Science", year: 2022, citations: 47 },
        { id: "p9", title: "Federated Learning Privacy Guarantees", journal: "Privacy in Machine Learning", year: 2021, citations: 36 },
      ],
      mutualConnections: [
        { id: "m5", name: "Prof. David Kim", university: "Harvard University", relationship: "Co-PI on NSF grant" },
      ]
    },
    { 
      id: "4", 
      name: "Prof. David Kim", 
      university: "Harvard University", 
      totalCitations: 198,
      titles: ["ACM Distinguished Scientist", "Associate Professor", "DARPA Young Faculty Award"],
      recentPapers: [
        { id: "p10", title: "Explainable AI for Healthcare", journal: "Nature Medicine", year: 2023, citations: 31 },
        { id: "p11", title: "Bias Mitigation in Machine Learning", journal: "Journal of AI Research", year: 2022, citations: 42 },
        { id: "p12", title: "Human-AI Collaboration Frameworks", journal: "Human-Computer Interaction", year: 2021, citations: 28 },
      ],
      mutualConnections: [
        { id: "m6", name: "Dr. Emily Rodriguez", university: "UC Berkeley", relationship: "Co-PI on NSF grant" },
        { id: "m7", name: "Dr. Sophia Patel", university: "University of Cambridge", relationship: "Former postdoc" },
      ]
    },
    { 
      id: "5", 
      name: "Dr. Lisa Wang", 
      university: "University of Oxford", 
      totalCitations: 176,
      titles: ["Royal Society Fellow", "Associate Professor", "ERC Grant Recipient"],
      recentPapers: [
        { id: "p13", title: "Generative Models for Scientific Discovery", journal: "Science Advances", year: 2023, citations: 24 },
        { id: "p14", title: "AI for Climate Change Modeling", journal: "Nature Climate Change", year: 2022, citations: 37 },
        { id: "p15", title: "Uncertainty Quantification in Deep Learning", journal: "Journal of Machine Learning Research", year: 2021, citations: 29 },
      ],
      mutualConnections: [
        { id: "m8", name: "Prof. Michael Chen", university: "MIT", relationship: "Former PhD student" },
        { id: "m9", name: "Prof. Thomas Lee", university: "University of Toronto", relationship: "Research collaborator" },
      ]
    },
    { 
      id: "6", 
      name: "Prof. James Wilson", 
      university: "ETH Zurich", 
      totalCitations: 163,
      titles: ["ELLIS Fellow", "Full Professor", "Swiss NSF Investigator"],
      recentPapers: [
        { id: "p16", title: "Robust Optimization for Deep Learning", journal: "SIAM Journal on Optimization", year: 2023, citations: 19 },
        { id: "p17", title: "Theoretical Foundations of Graph Neural Networks", journal: "Journal of Machine Learning Research", year: 2022, citations: 34 },
        { id: "p18", title: "Causal Inference in Time Series Analysis", journal: "Annals of Statistics", year: 2021, citations: 27 },
      ],
      mutualConnections: [
        { id: "m10", name: "Dr. Sarah Johnson", university: "Stanford University", relationship: "Co-author on 3 papers" },
        { id: "m11", name: "Dr. Emma Brown", university: "Imperial College London", relationship: "Former colleague" },
      ]
    },
    { 
      id: "7", 
      name: "Dr. Sophia Patel", 
      university: "University of Cambridge", 
      totalCitations: 154,
      titles: ["Royal Society University Research Fellow", "Assistant Professor", "Alan Turing Institute Fellow"],
      recentPapers: [
        { id: "p19", title: "Bayesian Deep Learning Methods", journal: "Bayesian Analysis", year: 2023, citations: 22 },
        { id: "p20", title: "Privacy-Preserving Machine Learning", journal: "Proceedings on Privacy Enhancing Technologies", year: 2022, citations: 31 },
        { id: "p21", title: "Fairness in Recommendation Systems", journal: "ACM Transactions on Information Systems", year: 2021, citations: 26 },
      ],
      mutualConnections: [
        { id: "m12", name: "Prof. David Kim", university: "Harvard University", relationship: "Former advisor" },
      ]
    },
    { 
      id: "8", 
      name: "Prof. Robert Garcia", 
      university: "University of Tokyo", 
      totalCitations: 142,
      titles: ["JSPS Fellow", "Associate Professor", "ACM Senior Member"],
      recentPapers: [
        { id: "p22", title: "Multimodal Learning for Robotics", journal: "IEEE Robotics and Automation Letters", year: 2023, citations: 18 },
        { id: "p23", title: "Human-Robot Interaction Paradigms", journal: "ACM Transactions on Human-Robot Interaction", year: 2022, citations: 29 },
        { id: "p24", title: "Reinforcement Learning in Dynamic Environments", journal: "Machine Learning", year: 2021, citations: 24 },
      ],
      mutualConnections: [
        { id: "m13", name: "Prof. Michael Chen", university: "MIT", relationship: "Conference committee member" },
        { id: "m14", name: "Dr. Olivia Martinez", university: "National University of Singapore", relationship: "Research collaborator" },
      ]
    },
    { 
      id: "9", 
      name: "Dr. Olivia Martinez", 
      university: "National University of Singapore", 
      totalCitations: 137,
      titles: ["NRF Fellow", "Assistant Professor", "IEEE Senior Member"],
      recentPapers: [
        { id: "p25", title: "Secure Federated Learning Systems", journal: "IEEE Transactions on Information Forensics and Security", year: 2023, citations: 17 },
        { id: "p26", title: "Edge Computing for IoT Applications", journal: "IEEE Internet of Things Journal", year: 2022, citations: 28 },
        { id: "p27", title: "Distributed Machine Learning Algorithms", journal: "Distributed Computing", year: 2021, citations: 23 },
      ],
      mutualConnections: [
        { id: "m15", name: "Prof. Robert Garcia", university: "University of Tokyo", relationship: "Research collaborator" },
      ]
    },
    { 
      id: "10", 
      name: "Prof. Thomas Lee", 
      university: "University of Toronto", 
      totalCitations: 129,
      titles: ["CIFAR AI Chair", "Associate Professor", "NSERC Discovery Grant Holder"],
      recentPapers: [
        { id: "p28", title: "Neural Architecture Search Methods", journal: "IEEE Transactions on Neural Networks and Learning Systems", year: 2023, citations: 16 },
        { id: "p29", title: "Self-Supervised Learning for Computer Vision", journal: "International Journal of Computer Vision", year: 2022, citations: 27 },
        { id: "p30", title: "Continual Learning Approaches", journal: "Neural Computation", year: 2021, citations: 22 },
      ],
      mutualConnections: [
        { id: "m16", name: "Dr. Lisa Wang", university: "University of Oxford", relationship: "Research collaborator" },
        { id: "m17", name: "Dr. Ava Williams", university: "University of Michigan", relationship: "Former PhD student" },
      ]
    },
    { 
      id: "11", 
      name: "Dr. Emma Brown", 
      university: "Imperial College London", 
      totalCitations: 118,
      titles: ["UKRI Future Leaders Fellow", "Lecturer", "Royal Society Dorothy Hodgkin Fellow"],
      recentPapers: [
        { id: "p31", title: "AI for Drug Discovery", journal: "Nature Machine Intelligence", year: 2023, citations: 15 },
        { id: "p32", title: "Machine Learning for Materials Science", journal: "npj Computational Materials", year: 2022, citations: 25 },
        { id: "p33", title: "Interpretable Models for Healthcare", journal: "Nature Medicine", year: 2021, citations: 21 },
      ],
      mutualConnections: [
        { id: "m18", name: "Prof. James Wilson", university: "ETH Zurich", relationship: "Former colleague" },
      ]
    },
    { 
      id: "12", 
      name: "Prof. Daniel Smith", 
      university: "Tsinghua University", 
      totalCitations: 112,
      titles: ["NSFC Distinguished Young Scholar", "Associate Professor", "IEEE Member"],
      recentPapers: [
        { id: "p34", title: "Efficient Transformers for NLP", journal: "Transactions of the Association for Computational Linguistics", year: 2023, citations: 14 },
        { id: "p35", title: "Knowledge Graphs for Reasoning", journal: "Journal of Web Semantics", year: 2022, citations: 24 },
        { id: "p36", title: "Cross-lingual Transfer Learning", journal: "Computational Linguistics", year: 2021, citations: 20 },
      ],
      mutualConnections: [
        { id: "m19", name: "Prof. Alexander Davis", university: "Technical University of Munich", relationship: "Research collaborator" },
      ]
    },
    { 
      id: "13", 
      name: "Dr. Ava Williams", 
      university: "University of Michigan", 
      totalCitations: 105,
      titles: ["NSF CAREER Award", "Assistant Professor", "Microsoft Research Faculty Fellow"],
      recentPapers: [
        { id: "p37", title: "Adversarial Machine Learning Defenses", journal: "IEEE Transactions on Information Forensics and Security", year: 2023, citations: 13 },
        { id: "p38", title: "Robust Deep Learning for Security", journal: "Journal of Cybersecurity", year: 2022, citations: 22 },
        { id: "p39", title: "Privacy-Preserving Analytics", journal: "Proceedings on Privacy Enhancing Technologies", year: 2021, citations: 19 },
      ],
      mutualConnections: [
        { id: "m20", name: "Prof. Thomas Lee", university: "University of Toronto", relationship: "Former advisor" },
      ]
    },
    { 
      id: "14", 
      name: "Prof. Alexander Davis", 
      university: "Technical University of Munich", 
      totalCitations: 98,
      titles: ["ERC Starting Grant Recipient", "Associate Professor", "DFG Emmy Noether Group Leader"],
      recentPapers: [
        { id: "p40", title: "Trustworthy AI Systems", journal: "AI Magazine", year: 2023, citations: 12 },
        { id: "p41", title: "Verification of Neural Networks", journal: "Journal of Automated Reasoning", year: 2022, citations: 21 },
        { id: "p42", title: "Formal Methods for AI Safety", journal: "Formal Aspects of Computing", year: 2021, citations: 18 },
      ],
      mutualConnections: [
        { id: "m21", name: "Prof. Daniel Smith", university: "Tsinghua University", relationship: "Research collaborator" },
        { id: "m22", name: "Dr. Natalie Taylor", university: "University of Edinburgh", relationship: "Co-author on 2 papers" },
      ]
    },
    { 
      id: "15", 
      name: "Dr. Natalie Taylor", 
      university: "University of Edinburgh", 
      totalCitations: 92,
      titles: ["UKRI Innovation Fellow", "Lecturer", "Royal Society University Research Fellow"],
      recentPapers: [
        { id: "p43", title: "Natural Language Processing for Scientific Literature", journal: "Journal of Biomedical Informatics", year: 2023, citations: 11 },
        { id: "p44", title: "Text Mining in Healthcare", journal: "BMC Medical Informatics and Decision Making", year: 2022, citations: 20 },
        { id: "p45", title: "Automated Medical Diagnosis Systems", journal: "Artificial Intelligence in Medicine", year: 2021, citations: 17 },
      ],
      mutualConnections: [
        { id: "m23", name: "Prof. Alexander Davis", university: "Technical University of Munich", relationship: "Co-author on 2 papers" },
      ]
    },
  ];

export default function CiterDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [citer, setCiter] = useState<CiterData | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch citer details
  useEffect(() => {
    if (id) {
      // In a real app, fetch from API
      // Find citer by matching the id string with the id property in the array
      const foundCiter = sampleCiters.find(citer => citer.id === id);
      setCiter(foundCiter || null);
      setLoading(false);
    }
  }, [id]);

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
                {citer.titles && citer.titles.length > 0 && (
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">Titles</dt>
                    <dd className="text-lg">
                      {citer.titles.map((title, index) => (
                        <span key={index} className="inline-block px-2 py-1 mr-2 mb-2 bg-blue-100 text-blue-800 rounded-full text-xs">
                          {title}
                        </span>
                      ))}
                    </dd>
                  </div>
                )}
              </dl>
            </CardContent>
          </Card>
        )}
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Papers</CardTitle>
              <CardDescription>Latest publications by this researcher</CardDescription>
            </div>
            <Button 
              variant="destructive"
              onClick={(e) => {
                e.preventDefault();
                console.log("Pull latest data clicked");
              }}
            >
              Pull Latest Data
            </Button>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Title</TableHead>
                    <TableHead>Journal</TableHead>
                    <TableHead>Year</TableHead>
                    <TableHead>Citations</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={4} className="h-24 text-center">
                        <ReloadIcon className="h-5 w-5 animate-spin mx-auto" />
                      </TableCell>
                    </TableRow>
                  ) : !citer?.recentPapers || citer.recentPapers.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} className="h-24 text-center">
                        No recent papers found for this researcher.
                      </TableCell>
                    </TableRow>
                  ) : (
                    citer.recentPapers.map((paper) => (
                      <TableRow key={paper.id}>
                        <TableCell className="font-medium">{paper.title}</TableCell>
                        <TableCell>{paper.journal}</TableCell>
                        <TableCell>{paper.year}</TableCell>
                        <TableCell>{paper.citations}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Mutual Connections</CardTitle>
            <CardDescription>Your connections with this researcher</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>University</TableHead>
                    <TableHead>Relationship</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={3} className="h-24 text-center">
                        <ReloadIcon className="h-5 w-5 animate-spin mx-auto" />
                      </TableCell>
                    </TableRow>
                  ) : !citer?.mutualConnections || citer.mutualConnections.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={3} className="h-24 text-center">
                        No mutual connections found with this researcher.
                      </TableCell>
                    </TableRow>
                  ) : (
                    citer.mutualConnections.map((connection) => (
                      <TableRow key={connection.id}>
                        <TableCell className="font-medium">{connection.name}</TableCell>
                        <TableCell>{connection.university}</TableCell>
                        <TableCell>{connection.relationship}</TableCell>
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