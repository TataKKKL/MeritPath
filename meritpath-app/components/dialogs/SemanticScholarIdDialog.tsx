import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createClient } from "@/utils/supabase/component";
import { makeApiAuthRequest } from "@/utils/auth/authApiHandler";

interface SemanticScholarIdDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
  userId: string;
}

export default function SemanticScholarIdDialog({
  open,
  onOpenChange,
  onSuccess,
  userId,
}: SemanticScholarIdDialogProps) {
  const [semanticScholarId, setSemanticScholarId] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const supabase = createClient();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!semanticScholarId.trim()) {
      setError("Please enter a valid Semantic Scholar ID");
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Get the session which contains the access token
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        throw new Error("No valid session found");
      }
      
      // Use makeApiAuthRequest with the correct endpoint
      await makeApiAuthRequest(
        session.access_token,
        `/api/users/${userId}/semantic-scholar-id`,
        {
          method: 'PUT',
          body: JSON.stringify({ semantic_scholar_id: semanticScholarId })
        }
      );
      
      onSuccess();
      onOpenChange(false);
    } catch (err) {
      console.error("Error updating Semantic Scholar ID:", err);
      setError(err instanceof Error ? err.message : "Failed to update Semantic Scholar ID");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Set Your Semantic Scholar ID</DialogTitle>
          <DialogDescription>
            Please enter your Semantic Scholar ID to enable personalized features.
            You can find your ID by visiting your profile on Semantic Scholar.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="semantic-scholar-id" className="col-span-4">
                Semantic Scholar ID
              </Label>
              <Input
                id="semantic-scholar-id"
                value={semanticScholarId}
                onChange={(e) => setSemanticScholarId(e.target.value)}
                placeholder="e.g., 51453144"
                className="col-span-4"
                required
              />
            </div>
            {error && (
              <div className="text-red-500 text-sm">{error}</div>
            )}
          </div>
          <DialogFooter>
            <Button 
              type="submit" 
              disabled={isSubmitting}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isSubmitting ? "Saving..." : "Save"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
} 