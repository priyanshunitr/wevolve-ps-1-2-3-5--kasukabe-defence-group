"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { AuthProvider } from "@/contexts/AuthContext";
import { ResumeProvider } from "@/contexts/ResumeContext";
import { SavedJobsProvider } from "@/contexts/SavedJobsContext";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";

const queryClient = new QueryClient();

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider>
                <AuthProvider>
                    <ResumeProvider>
                        <SavedJobsProvider>
                            <TooltipProvider>
                                <Toaster />
                                <Sonner />
                                {children}
                            </TooltipProvider>
                        </SavedJobsProvider>
                    </ResumeProvider>
                </AuthProvider>
            </ThemeProvider>
        </QueryClientProvider>
    );
}
