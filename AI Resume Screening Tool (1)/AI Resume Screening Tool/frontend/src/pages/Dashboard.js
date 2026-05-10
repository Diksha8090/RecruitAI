import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  HiOutlineUsers, HiOutlineBriefcase, HiOutlineTrendingUp,
  HiOutlineCheckCircle, HiOutlineArrowRight, HiOutlineSparkles,
  HiOutlineClock, HiOutlineChartBar
} from 'react-icons/hi';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import Topbar from '../components/Topbar';
import { resumeAPI, jobAPI } from '../services';
import useAuthStore from '../store/authStore';

const COLORS = ['#00D4AA', '#F59E0B', '#EF4444', '#8B5CF6'];

const fadeUp = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } };
const container = { hidden: {}, show: { transition: { staggerChildren: 0.07 } } };

function StatCard({ icon: Icon, label, value, sub, color = 'teal' }) {
  const colors = {
    teal: 'text-teal bg-teal/10 border-teal/20',
    orange: 'text-brand-orange bg-brand-orange/10 border-brand-orange/20',
    purple: 'text-brand-purple bg-brand-purple/10 border-brand-purple/20',
    blue: 'text-brand-blue bg-brand-blue/10 border-brand-blue/20',
  };
  return (
    <motion.div variants={fadeUp} className="card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">{label}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
        </div>
        <div className={`w-10 h-10 rounded-lg border flex items-center justify-center ${colors[color]}`}>
          <Icon className="text-lg" />
        </div>
      </div>
    </motion.div>
  );
}

export default function Dashboard() {
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([resumeAPI.getAll(), jobAPI.getAll()])
      .then(([r, j]) => {
        setResumes(r.data.resumes || []);
        setJobs(j.data.job_postings || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const analyzed = resumes.filter(r => r.analyses?.length > 0);
  const highlyQ = resumes.filter(r => r.analyses?.[0]?.category === 'Highly Qualified');

  const categoryData = [
    { name: 'Highly Qualified', value: resumes.filter(r => r.analyses?.[0]?.category === 'Highly Qualified').length },
    { name: 'Qualified', value: resumes.filter(r => r.analyses?.[0]?.category === 'Qualified').length },
    { name: 'Not a Fit', value: resumes.filter(r => r.analyses?.[0]?.category === 'Not a Fit').length },
  ].filter(d => d.value > 0);

  const scoreData = resumes
    .filter(r => r.analyses?.[0]?.match_score)
    .slice(0, 8)
    .map(r => ({
      name: (r.candidate_name || 'Unknown').split(' ')[0],
      score: Math.round(r.analyses[0].match_score)
    }));

  return (
    <div className="flex flex-col h-full">
      <Topbar
        title={`Welcome back, ${user?.username || 'Admin'}! 👋`}
        subtitle="Here's your AI-powered hiring overview"
      />

      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Stats */}
        <motion.div variants={container} initial="hidden" animate="show"
          className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard icon={HiOutlineUsers} label="Total Candidates" value={resumes.length} sub="All uploads" color="teal" />
          <StatCard icon={HiOutlineBriefcase} label="Open Positions" value={jobs.length} sub="Active jobs" color="orange" />
          <StatCard icon={HiOutlineChartBar} label="Analyzed" value={analyzed.length} sub="With AI scores" color="purple" />
          <StatCard icon={HiOutlineCheckCircle} label="Top Matches" value={highlyQ.length} sub="Highly qualified" color="blue" />
        </motion.div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Bar chart */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
            className="card lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-white">Candidate Match Scores</h3>
                <p className="text-xs text-gray-500">AI-generated fit scores</p>
              </div>
              <HiOutlineTrendingUp className="text-teal text-xl" />
            </div>
            {scoreData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={scoreData} barSize={28}>
                  <XAxis dataKey="name" tick={{ fill: '#8B949E', fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis domain={[0, 100]} tick={{ fill: '#8B949E', fontSize: 12 }} axisLine={false} tickLine={false} />
                  <Tooltip
                    contentStyle={{ background: '#1C2333', border: '1px solid #30363D', borderRadius: 8, color: '#fff' }}
                    cursor={{ fill: 'rgba(0,212,170,0.05)' }}
                  />
                  <Bar dataKey="score" fill="#00D4AA" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[200px] flex items-center justify-center text-gray-500 text-sm">
                No analyzed candidates yet. Upload and analyze resumes to see scores.
              </div>
            )}
          </motion.div>

          {/* Pie chart */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
            className="card">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-white">Category Breakdown</h3>
                <p className="text-xs text-gray-500">Qualification categories</p>
              </div>
            </div>
            {categoryData.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={160}>
                  <PieChart>
                    <Pie data={categoryData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} dataKey="value" paddingAngle={3}>
                      {categoryData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                    </Pie>
                    <Tooltip contentStyle={{ background: '#1C2333', border: '1px solid #30363D', borderRadius: 8, color: '#fff' }} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="space-y-2 mt-2">
                  {categoryData.map((d, i) => (
                    <div key={d.name} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-2.5 h-2.5 rounded-full" style={{ background: COLORS[i] }} />
                        <span className="text-gray-400">{d.name}</span>
                      </div>
                      <span className="text-white font-medium">{d.value}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="h-[200px] flex items-center justify-center text-gray-500 text-sm text-center">
                Analyze resumes to see category breakdown
              </div>
            )}
          </motion.div>
        </div>

        {/* Recent candidates */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
          className="card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-white">Recent Candidates</h3>
              <p className="text-xs text-gray-500">Latest uploads</p>
            </div>
            <button onClick={() => navigate('/candidates')} className="flex items-center gap-1 text-xs text-teal hover:underline">
              View all <HiOutlineArrowRight />
            </button>
          </div>

          {loading ? (
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-14 bg-dark-600 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : resumes.length === 0 ? (
            <div className="text-center py-10">
              <HiOutlineUsers className="text-4xl text-gray-600 mx-auto mb-3" />
              <p className="text-gray-500 mb-4">No candidates yet</p>
              <button onClick={() => navigate('/candidates')} className="btn-primary">
                <HiOutlineSparkles /> Upload Resumes
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              {resumes.slice(0, 6).map(r => {
                const analysis = r.analyses?.[0];
                const score = analysis?.match_score ? Math.round(analysis.match_score) : null;
                const cat = analysis?.category;
                return (
                  <motion.div key={r.id} whileHover={{ x: 2 }}
                    onClick={() => navigate(`/candidates/${r.id}`)}
                    className="flex items-center justify-between p-3 rounded-lg bg-dark-600 hover:bg-dark-500 cursor-pointer transition-all">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 bg-gradient-to-br from-teal/20 to-brand-blue/20 rounded-lg flex items-center justify-center border border-dark-500">
                        <span className="text-teal font-bold text-sm">
                          {(r.candidate_name || '?')[0].toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">{r.candidate_name || 'Unknown'}</p>
                        <p className="text-xs text-gray-500">{r.email || r.file_type?.toUpperCase()}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {score !== null && (
                        <div className="text-right">
                          <p className="text-sm font-bold text-teal">{score}%</p>
                          <p className="text-xs text-gray-500">match</p>
                        </div>
                      )}
                      {cat && (
                        <span className={cat === 'Highly Qualified' ? 'badge-high' : cat === 'Qualified' ? 'badge-medium' : 'badge-low'}>
                          {cat}
                        </span>
                      )}
                      {!analysis && <span className="badge-blue flex items-center gap-1"><HiOutlineClock className="text-xs" /> Pending</span>}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </motion.div>

        {/* Quick actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { label: 'Post a Job', desc: 'Create a new job posting', path: '/jobs', icon: HiOutlineBriefcase, color: 'from-teal/20 to-brand-blue/20' },
            { label: 'Upload Resumes', desc: 'Bulk upload and screen', path: '/candidates', icon: HiOutlineUsers, color: 'from-brand-orange/20 to-brand-pink/20' },
            { label: 'Ask AI', desc: 'Query your hiring data', path: '/chat', icon: HiOutlineSparkles, color: 'from-brand-purple/20 to-brand-blue/20' },
          ].map(({ label, desc, path, icon: Icon, color }) => (
            <motion.div key={label} variants={fadeUp} whileHover={{ y: -2 }}
              onClick={() => navigate(path)}
              className={`card cursor-pointer bg-gradient-to-br ${color} border-dark-500 hover:border-teal/40 transition-all`}>
              <Icon className="text-2xl text-white mb-3" />
              <p className="font-semibold text-white mb-1">{label}</p>
              <p className="text-xs text-gray-400">{desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
