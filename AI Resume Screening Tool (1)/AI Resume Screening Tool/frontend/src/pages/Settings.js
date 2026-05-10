import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { HiOutlineCog, HiOutlineUser, HiOutlineKey, HiOutlineSparkles, HiOutlineShieldCheck } from 'react-icons/hi';
import toast from 'react-hot-toast';
import Topbar from '../components/Topbar';
import useAuthStore from '../store/authStore';

export default function Settings() {
  const { user } = useAuthStore();
  const [aiModel, setAiModel] = useState(localStorage.getItem('ai_model') || 'openrouter');
  const [blindDefault, setBlindDefault] = useState(localStorage.getItem('blind_default') === 'true');

  const savePrefs = () => {
    localStorage.setItem('ai_model', aiModel);
    localStorage.setItem('blind_default', String(blindDefault));
    toast.success('Preferences saved');
  };

  return (
    <div className="flex flex-col h-full">
      <Topbar title="Settings" subtitle="Manage your account and preferences" />

      <div className="flex-1 p-6 space-y-5 max-w-2xl overflow-y-auto">
        {/* Profile */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2"><HiOutlineUser className="text-teal" /> Profile</h3>
          <div className="flex items-center gap-4 mb-4">
            <div className="w-14 h-14 bg-gradient-to-br from-teal to-brand-blue rounded-xl flex items-center justify-center">
              <span className="text-dark-900 font-bold text-xl">{(user?.username || 'U')[0].toUpperCase()}</span>
            </div>
            <div>
              <p className="font-semibold text-white">{user?.username}</p>
              <p className="text-sm text-gray-500">{user?.email}</p>
              {user?.organization && <p className="text-xs text-gray-600">{user.organization}</p>}
            </div>
          </div>
        </div>

        {/* AI Preferences */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2"><HiOutlineSparkles className="text-brand-orange" /> AI Preferences</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Default AI Model</label>
              <select className="input" value={aiModel} onChange={e => setAiModel(e.target.value)}>
                <option value="openrouter">OpenRouter Free Router (Recommended)</option>
                <option value="gemini">Google Gemini 2.5 Flash</option>
                <option value="openai">OpenAI GPT-4o Mini</option>
                <option value="mock">Local fallback</option>
              </select>
              <p className="text-xs text-gray-600 mt-1">Used for resume analysis and chat</p>
            </div>
            <div className="flex items-center justify-between py-3 border-t border-dark-500">
              <div>
                <p className="text-sm font-medium text-white">Blind Screening by Default</p>
                <p className="text-xs text-gray-500">Remove PII before AI analysis to reduce bias</p>
              </div>
              <div className={`w-10 h-5 rounded-full transition-colors relative cursor-pointer ${blindDefault ? 'bg-teal' : 'bg-dark-500'}`}
                onClick={() => setBlindDefault(b => !b)}>
                <div className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${blindDefault ? 'translate-x-5' : ''}`} />
              </div>
            </div>
          </div>
          <motion.button whileTap={{ scale: 0.97 }} onClick={savePrefs} className="btn-primary mt-4">
            <HiOutlineCog /> Save Preferences
          </motion.button>
        </div>

        {/* API Keys Info */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2"><HiOutlineKey className="text-brand-purple" /> API Configuration</h3>
          <p className="text-sm text-gray-500 mb-3">API keys are configured in the backend <code className="bg-dark-600 px-1.5 py-0.5 rounded text-teal text-xs">.env</code> file.</p>
          <div className="space-y-2">
            {[
              { label: 'OpenAI API Key', status: 'Configured', color: 'emerald' },
              { label: 'Google Gemini API Key', status: 'Configured', color: 'emerald' },
              { label: 'GitHub Token', status: 'Optional', color: 'amber' },
            ].map(({ label, status, color }) => (
              <div key={label} className="flex items-center justify-between py-2">
                <span className="text-sm text-gray-400">{label}</span>
                <span className={`text-xs font-medium ${color === 'emerald' ? 'text-emerald-400' : 'text-amber-400'}`}>{status}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Bias */}
        <div className="card bg-gradient-to-br from-brand-purple/10 to-brand-blue/10 border-brand-purple/20">
          <div className="flex items-center gap-2 mb-2">
            <HiOutlineShieldCheck className="text-brand-purple text-lg" />
            <h3 className="font-semibold text-white">Bias Detection</h3>
          </div>
          <p className="text-sm text-gray-400">
            RecruitAI automatically detects gender, age, location, and education bias in resumes.
            Enable blind screening to remove personal identifiers before AI analysis for fairer hiring decisions.
          </p>
        </div>
      </div>
    </div>
  );
}
