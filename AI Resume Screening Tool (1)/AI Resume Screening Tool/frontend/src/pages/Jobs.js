import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  HiOutlineBriefcase, HiOutlinePlus, HiOutlineX, HiOutlinePencil,
  HiOutlineTrash, HiOutlineLocationMarker, HiOutlineCurrencyDollar,
  HiOutlineClock, HiOutlineUsers
} from 'react-icons/hi';
import toast from 'react-hot-toast';
import Topbar from '../components/Topbar';
import { jobAPI } from '../services';

const EMPTY = { title: '', description: '', requirements: '', skills: '', experience_required: '', location: '', salary_range: '' };

function JobModal({ job, onClose, onSave }) {
  const [form, setForm] = useState(job || EMPTY);
  const [loading, setLoading] = useState(false);
  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title || !form.description) return toast.error('Title and description are required');
    setLoading(true);
    try {
      if (job) {
        await jobAPI.update(job.id, form);
        toast.success('Job updated');
      } else {
        await jobAPI.create(form);
        toast.success('Job created');
      }
      onSave();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to save job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }}
        className="bg-dark-800 border border-dark-500 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between p-6 border-b border-dark-500">
          <div>
            <h2 className="text-lg font-bold text-white">{job ? 'Edit Job' : 'New Job Posting'}</h2>
            <p className="text-xs text-gray-500 mt-0.5">Fill in the details for AI-powered candidate matching</p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors p-1">
            <HiOutlineX className="text-xl" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Job Title <span className="text-teal">*</span></label>
              <input className="input" placeholder="e.g. Senior React Developer" value={form.title} onChange={set('title')} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Location</label>
              <input className="input" placeholder="e.g. Remote / Mumbai" value={form.location} onChange={set('location')} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Experience Required</label>
              <input className="input" placeholder="e.g. 3-5 years" value={form.experience_required} onChange={set('experience_required')} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Salary Range</label>
              <input className="input" placeholder="e.g. ₹12-18 LPA" value={form.salary_range} onChange={set('salary_range')} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Required Skills</label>
              <input className="input" placeholder="React, Node.js, TypeScript (comma-separated)" value={form.skills} onChange={set('skills')} />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Job Description <span className="text-teal">*</span></label>
              <textarea className="input resize-none" rows={4} placeholder="Describe the role and responsibilities..."
                value={form.description} onChange={set('description')} required />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Requirements & Qualifications</label>
              <textarea className="input resize-none" rows={3} placeholder="Bachelor's degree, 3+ years experience..."
                value={form.requirements} onChange={set('requirements')} />
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1 justify-center">Cancel</button>
            <button type="submit" disabled={loading} className="btn-primary flex-1 justify-center">
              {loading ? 'Saving...' : job ? 'Update Job' : 'Create Job'}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}

function JobCard({ job, onEdit, onDelete }) {
  const skills = job.skills ? job.skills.split(',').map(s => s.trim()).filter(Boolean) : [];
  return (
    <motion.div variants={{ hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } }}
      whileHover={{ y: -2 }} className="card-hover">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-brand-orange/20 to-brand-pink/20 rounded-lg flex items-center justify-center border border-dark-500">
            <HiOutlineBriefcase className="text-brand-orange text-lg" />
          </div>
          <div>
            <h3 className="font-semibold text-white">{job.title}</h3>
            <p className="text-xs text-gray-500">{new Date(job.created_at).toLocaleDateString()}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={() => onEdit(job)} className="w-8 h-8 flex items-center justify-center rounded-lg bg-dark-600 text-gray-400 hover:text-teal hover:bg-teal/10 transition-all">
            <HiOutlinePencil className="text-sm" />
          </button>
          <button onClick={() => onDelete(job.id)} className="w-8 h-8 flex items-center justify-center rounded-lg bg-dark-600 text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all">
            <HiOutlineTrash className="text-sm" />
          </button>
        </div>
      </div>

      <p className="text-sm text-gray-400 line-clamp-2 mb-4">{job.description}</p>

      <div className="flex flex-wrap gap-2 mb-4">
        {skills.slice(0, 5).map(s => (
          <span key={s} className="bg-dark-600 border border-dark-500 text-gray-300 text-xs px-2.5 py-1 rounded-full">{s}</span>
        ))}
        {skills.length > 5 && <span className="text-xs text-gray-500">+{skills.length - 5} more</span>}
      </div>

      <div className="flex items-center gap-4 text-xs text-gray-500 pt-3 border-t border-dark-500">
        {job.location && <span className="flex items-center gap-1"><HiOutlineLocationMarker />{job.location}</span>}
        {job.experience_required && <span className="flex items-center gap-1"><HiOutlineClock />{job.experience_required}</span>}
        {job.salary_range && <span className="flex items-center gap-1"><HiOutlineCurrencyDollar />{job.salary_range}</span>}
      </div>
    </motion.div>
  );
}

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(null); // null | 'create' | job object

  const load = async () => {
    try {
      const res = await jobAPI.getAll();
      setJobs(res.data.job_postings || []);
    } catch {
      toast.error('Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this job posting?')) return;
    try {
      await jobAPI.delete(id);
      toast.success('Job deleted');
      setJobs(j => j.filter(x => x.id !== id));
    } catch {
      toast.error('Failed to delete');
    }
  };

  return (
    <div className="flex flex-col h-full">
      <Topbar title="Job Postings" subtitle="Manage your open positions" />

      <div className="flex-1 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <span className="badge-blue">{jobs.length} positions</span>
          </div>
          <button onClick={() => setModal('create')} className="btn-primary">
            <HiOutlinePlus /> New Job
          </button>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => <div key={i} className="card h-52 animate-pulse" />)}
          </div>
        ) : jobs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <HiOutlineBriefcase className="text-5xl text-gray-600 mb-4" />
            <p className="text-gray-400 text-lg font-medium mb-2">No job postings yet</p>
            <p className="text-gray-600 text-sm mb-6">Create your first job to start screening candidates</p>
            <button onClick={() => setModal('create')} className="btn-primary">
              <HiOutlinePlus /> Create Job Posting
            </button>
          </div>
        ) : (
          <motion.div initial="hidden" animate="show"
            variants={{ hidden: {}, show: { transition: { staggerChildren: 0.06 } } }}
            className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {jobs.map(job => (
              <JobCard key={job.id} job={job} onEdit={j => setModal(j)} onDelete={handleDelete} />
            ))}
          </motion.div>
        )}
      </div>

      <AnimatePresence>
        {modal && (
          <JobModal
            job={modal === 'create' ? null : modal}
            onClose={() => setModal(null)}
            onSave={() => { setModal(null); load(); }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
