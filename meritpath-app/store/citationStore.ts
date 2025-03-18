import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { createClient } from '@/utils/supabase/component';
import { makeApiAuthRequest } from '@/utils/auth/authApiHandler';

interface CitationState {
  citersProcessingStatus: 'not_started' | 'processing' | 'done';
  isEligibleForCitationAnalysis: boolean;
  setCitersProcessingStatus: (status: 'not_started' | 'processing' | 'done') => void;
  setIsEligibleForCitationAnalysis: (isEligible: boolean) => void;
  checkCitersStatus: (userId: string) => Promise<void>;
  resetState: () => void;
}

export const useCitationStore = create<CitationState>()(
  persist(
    (set, get) => ({
      citersProcessingStatus: 'not_started',
      isEligibleForCitationAnalysis: false,
      
      setCitersProcessingStatus: (status) => set({ citersProcessingStatus: status }),
      
      setIsEligibleForCitationAnalysis: (isEligible) => 
        set({ isEligibleForCitationAnalysis: isEligible }),
      
      checkCitersStatus: async (userId) => {
        try {
          const supabase = createClient();
          const { data: { session } } = await supabase.auth.getSession();
          
          if (session?.access_token) {
            const response = await makeApiAuthRequest(
              session.access_token,
              `/api/users/${userId}/job_done`,
              { method: 'GET' }
            );
            if (response.job_done) {
              set({ citersProcessingStatus: 'done' });
              console.log('citersProcessingStatus: ', get().citersProcessingStatus);
            }
          }
        } catch (error) {
          console.error('Error checking citers status:', error);
        }
      },
      
      resetState: () => set({ 
        citersProcessingStatus: 'not_started', 
        isEligibleForCitationAnalysis: false 
      }),
    }),
    {
      name: 'citation-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
); 