import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import {
  HiOutlineUpload, HiOutlineX, HiOutlineSearch, HiOutlineFilter,
  HiOutlineChartBar, HiOutlineUsers, HiOutlineTrash, HiOutlineEye,
  HiOutlineSparkles, HiOutlineCode, HiOutlineRefresh
} from 'react-icons/hi';
import toast from 'react-hot-toast';
import Topbar from '../components/Topbar';
import { resumeAPI, jobAPI, analysisAPI } from '../services';

function ScoreBadge({ score }) {
  if (score === null || score === undefined) return <span className="badge-blue">Pending</span>;
  if (score >= 75) return <span className="badge-high">{score}%</span>;
  if (score >= 50) return <span className="badge-medium">{score}%</span>;
  return <span className="badge-low">{score}%</span>;
}

function CategoryBadge({ cat }) {
  if (!cat) return null;
  if (cat === 'Highly Qualified') return <span className="badge-high">Highly Qualified</span>;
  if (cat === 'Qualified') return <span className="badge-medium">Qualified</span>;
  return <span className="badge-low">Not a Fit</span>;
}

function UploadZone({ onDrop, uploading }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] },
    multiple: true,
  });

  return (
    <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-300
      ${isDragActive ? 'border-teal bg-teal/5 scale-[1.01]' : 'border-dark-500 hover:border-teal/50 hover:bg-dark-700/50'}`}>
      <input {...getInputProps()} />
      <motion.div animate={{ y: isDragActive ? -6 : 0 }} transition={{ type: 'spring', stiffness: 300 }}>
        <HiOutlineUpload className={`text-4xl mx-auto mb-3 ${isDragActive ? 'text-teal' : 'text-gray-500'}`} />
        <p className="text-white font-medium mb-1">
          {isDragActive ? 'Drop resumes here!' : 'Drag & drop resumes'}
        </p>
        <p className="text-sm text-gray-500">or click to browse — PDF and DOCX supported</p>
        {uploading && (
          <div className="mt-4 flex items-center justify-center gap-2 text-teal text-sm">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Uploading...
          </div>
        )}
      </motion.div>
    </div>
  );
}

export default function Candidates() {
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [selectedJob, setSelectedJob] = useState('');
  const [selectedIds, setSelectedIds] = useState([]);
  const [aiModel, setAiModel] = useState(localStorage.getItem('ai_model') || 'gemini');
  const [blindMode, setBlindMode] = useState(false);
  const navigate = useNavigate();

  const load = async () => {
    try {
      const [r, j] = await Promise.all([resumeAPI.getAll(), jobAPI.getAll()]);
      setResumes(r.data.resumes || []);
      const jList = j.data.job_postings || [];
      setJobs(jList);
      if (jList.length > 0 && !selectedJob) setSelectedJob(String(jList[0].id));
    } catch { toast.error('Failed to load data'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const onDrop = useCallback(async (files) => {
    if (!files.length) return;
    setUploading(true);
    let uploaded = 0;
    for (const file of files) {
      try {
        const fd = new FormData();
        fd.append('file', file);
        await resumeAPI.upload(fd);
        uploaded++;
      } catch (err) {
        toast.error(`Failed: ${file.name}`);
      }
    }
    if (uploaded > 0) toast.success(`${uploaded} resume(s) uploaded`);
    setUploading(false);
    load();
  }, []);

  const handleBulkAnalyze = async () => {
    const ids = selectedIds.length > 0 ? selectedIds : resumes.map(r => r.id);
    if (!selectedJob) return toast.error('Select a job posting first');
    if (!ids.length) return toast.error('No resumes to analyze');
    setAnalyzing(true);
    try {
      await analysisAPI.bulkAnalyze({ resume_ids: ids, job_posting_id: Number(selectedJob), ai_model: aiModel, blind_mode: blindMode });
      toast.success(`Analyzed ${ids.length} resume(s)!`);
      setSelectedIds([]);
      await new Promise(resolve => setTimeout(resolve, 500));
      load();
      setTimeout(() => load(), 1000);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this candidate?')) return;
    try {
      await resumeAPI.delete(id);
      setResumes(r => r.filter(x => x.id !== id));
      toast.success('Candidate deleted');
    } catch { toast.error('Failed to delete'); }
  };

  const toggleSelect = (id) => {
    setSelectedIds(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);
  };

  const filtered = resumes.filter(r => {
    const name = (r.candidate_name || '').toLowerCase();
    const email = (r.email || '').toLowerCase();
    const matchSearch = name.includes(search.toLowerCase()) || email.includes(search.toLowerCase());
    const cat = r.analyses?.[0]?.category;
    const matchFilter =
      filter === 'all' ? true :
      filter === 'highly' ? cat === 'Highly Qualified' :
      filter === 'qualified' ? cat === 'Qualified' :
      filter === 'notfit' ? cat === 'Not a Fit' :
      filter === 'pending' ? !r.analyses?.length : true;
    return matchSearch && matchFilter;
  });

  const sorted = [...filtered].sort((a, b) => {
    const sa = a.analyses?.[0]?.match_score || 0;
    const sb = b.analyses?.[0]?.match_score || 0;
    return sb - sa;
  });

  return (
    <div className="flex flex-col h-full">
      <Topbar title="Candidates" subtitle="Upload, screen, and rank your applicants" />

      <div className="flex-1 p-6 space-y-5 overflow-y-auto">
        {/* Upload */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <HiOutlineUpload className="text-teal" /> Upload Resumes
          </h3>
          <UploadZone onDrop={onDrop} uploading={uploading} />
        </div>

        {/* Analysis controls */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <HiOutlineSparkles className="text-brand-orange" /> AI Analysis
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1.5">Job Posting</label>
              <select className="input text-sm" value={selectedJob} onChange={e => setSelectedJob(e.target.value)}>
                <option value="">Select job...</option>
                {jobs.map(j => <option key={j.id} value={j.id}>{j.title}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1.5">AI Model</label>
              <select className="input text-sm" value={aiModel} onChange={e => setAiModel(e.target.value)}>
                <option value="openrouter">OpenRouter Free Router</option>
                <option value="gemini">Google Gemini 2.5 Flash</option>
                <option value="mock">Local fallback</option>
              </select>
            </div>
            <div className="flex flex-col justify-end">
              <label className="flex items-center gap-2 cursor-pointer">
                <div className={`w-10 h-5 rounded-full transition-colors relative ${blindMode ? 'bg-teal' : 'bg-dark-500'}`}
                  onClick={() => setBlindMode(b => !b)}>
                  <div className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${blindMode ? 'translate-x-5' : ''}`} />
                </div>
                <span className="text-sm text-gray-300">Blind Mode</span>
              </label>
              <p className="text-xs text-gray-600 mt-1">Removes PII for fair screening</p>
            </div>
            <div className="flex flex-col justify-end">
              <motion.button
                whileTap={{ scale: 0.97 }}
                onClick={handleBulkAnalyze}
                disabled={analyzing || !selectedJob}
                className="btn-primary justify-center"
              >
                {analyzing ? (
                  <><svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg> Analyzing...</>
                ) : (
                  <><HiOutlineSparkles />
                    {selectedIds.length > 0 ? `Analyze ${selectedIds.length} selected` : 'Analyze All'}</>
                )}
              </motion.button>
            </div>
          </div>
          {blindMode && (
            <div className="bg-brand-purple/10 border border-brand-purple/30 rounded-lg px-4 py-2.5 text-sm text-brand-purple">
              Blind screening enabled — names, emails, phones, and addresses will be removed before AI analysis
            </div>
          )}
        </div>

        {/* Filter + Search */}
        <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
          <div className="flex gap-2 flex-wrap">
            {[
              { key: 'all', label: 'All' },
              { key: 'highly', label: 'Highly Qualified' },
              { key: 'qualified', label: 'Qualified' },
              { key: 'notfit', label: 'Not a Fit' },
              { key: 'pending', label: 'Pending' },
            ].map(({ key, label }) => (
              <button key={key} onClick={() => setFilter(key)}
                className={`text-xs px-3 py-1.5 rounded-full font-medium border transition-all ${filter === key
                  ? 'bg-teal text-dark-900 border-teal'
                  : 'bg-dark-700 text-gray-400 border-dark-500 hover:border-teal/50'}`}>
                {label}
              </button>
            ))}
          </div>
          <div className="relative">
            <HiOutlineSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm" />
            <input placeholder="Search candidates..." value={search} onChange={e => setSearch(e.target.value)}
              className="input pl-9 py-2 text-sm w-56" />
          </div>
        </div>

        {/* Candidate list */}
        {loading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => <div key={i} className="card h-20 animate-pulse" />)}
          </div>
        ) : sorted.length === 0 ? (
          <div className="card text-center py-12">
            <HiOutlineUsers className="text-5xl text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400 font-medium">{search || filter !== 'all' ? 'No matches found' : 'No candidates yet'}</p>
            <p className="text-sm text-gray-600 mt-1">Upload resumes above to get started</p>
          </div>
        ) : (
          <div className="space-y-2">
            {selectedIds.length > 0 && (
              <div className="flex items-center gap-3 bg-teal/10 border border-teal/30 rounded-lg px-4 py-2.5">
                <span className="text-sm text-teal font-medium">{selectedIds.length} selected</span>
                <button onClick={() => setSelectedIds([])} className="text-xs text-gray-500 hover:text-white ml-auto">Clear</button>
              </div>
            )}
            {sorted.map((r, idx) => {
              const analysis = r.analyses?.[0];
              const score = analysis?.match_score ? Math.round(analysis.match_score) : null;
              const isSelected = selectedIds.includes(r.id);

              return (
                <motion.div key={r.id}
                  initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.03 }}
                  className={`flex items-center gap-4 p-4 rounded-xl border transition-all cursor-pointer
                    ${isSelected ? 'border-teal bg-teal/5' : 'border-dark-500 bg-dark-700 hover:border-teal/40'}`}
                >
                  {/* Rank */}
                  <span className="w-7 text-center text-xs font-bold text-gray-600 flex-shrink-0">#{idx + 1}</span>

                  {/* Checkbox */}
                  <div onClick={() => toggleSelect(r.id)}
                    className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-all
                      ${isSelected ? 'bg-teal border-teal' : 'border-dark-500 hover:border-teal'}`}>
                    {isSelected && <HiOutlineX className="text-dark-900 text-xs" />}
                  </div>

                  {/* Avatar */}
                  <div className="w-10 h-10 bg-gradient-to-br from-teal/20 to-brand-blue/20 rounded-lg flex items-center justify-center border border-dark-500 flex-shrink-0">
                    <span className="text-teal font-bold">{(r.candidate_name || '?')[0].toUpperCase()}</span>
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0" onClick={() => navigate(`/candidates/${r.id}`)}>
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-white truncate">{r.candidate_name || 'Unknown Candidate'}</p>
                      {analysis?.github_url && <HiOutlineCode className="text-brand-purple text-sm flex-shrink-0" title="GitHub profile" />}
                    </div>
                    <p className="text-xs text-gray-500 truncate">{r.email || r.file_type?.toUpperCase()}</p>
                  </div>

                  {/* Scores */}
                  <div className="hidden sm:flex items-center gap-6 flex-shrink-0" onClick={() => navigate(`/candidates/${r.id}`)}>
                    {analysis && (
                      <>
                        <div className="text-center">
                          <p className="text-xs text-gray-500">Resume</p>
                          <p className="text-sm font-bold text-white">{analysis.resume_rating || '—'}/10</p>
                        </div>
                        {analysis.github_score > 0 && (
                          <div className="text-center">
                            <p className="text-xs text-gray-500">GitHub</p>
                            <p className="text-sm font-bold text-brand-purple">{Math.round(analysis.github_score)}</p>
                          </div>
                        )}
                      </>
                    )}
                    <ScoreBadge score={score} />
                    <CategoryBadge cat={analysis?.category} />
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 flex-shrink-0">
                    <button onClick={() => navigate(`/candidates/${r.id}`)}
                      className="w-8 h-8 flex items-center justify-center rounded-lg bg-dark-600 text-gray-400 hover:text-teal hover:bg-teal/10 transition-all">
                      <HiOutlineEye className="text-sm" />
                    </button>
                    <button onClick={() => handleDelete(r.id)}
                      className="w-8 h-8 flex items-center justify-center rounded-lg bg-dark-600 text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all">
                      <HiOutlineTrash className="text-sm" />
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
