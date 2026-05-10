import { create } from 'zustand';

const useResumeStore = create((set) => ({
  resumes: [],
  selectedResume: null,
  analyses: [],
  selectedAnalysis: null,

  setResumes: (resumes) => set({ resumes }),
  setSelectedResume: (resume) => set({ selectedResume: resume }),
  addResume: (resume) => set((state) => ({
    resumes: [...state.resumes, resume]
  })),
  deleteResume: (id) => set((state) => ({
    resumes: state.resumes.filter((r) => r.id !== id)
  })),

  setAnalyses: (analyses) => set({ analyses }),
  setSelectedAnalysis: (analysis) => set({ selectedAnalysis: analysis }),
  addAnalysis: (analysis) => set((state) => ({
    analyses: [...state.analyses, analysis]
  })),
}));

export default useResumeStore;
