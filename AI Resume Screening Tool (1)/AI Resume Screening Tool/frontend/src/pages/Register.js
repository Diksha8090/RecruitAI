import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiOutlineMail, HiOutlineLockClosed, HiOutlineUser, HiOutlineOfficeBuilding, HiOutlineSparkles } from 'react-icons/hi';
import toast from 'react-hot-toast';
import { authAPI } from '../services';

export default function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '', organization: '' });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.email || !form.password) return toast.error('Fill in required fields');
    if (form.password.length < 6) return toast.error('Password must be at least 6 characters');
    setLoading(true);
    try {
      await authAPI.register(form);
      toast.success('Account created! Please sign in.');
      navigate('/login');
    } catch (err) {
      toast.error(err.response?.data?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    { key: 'username', label: 'Username', placeholder: 'johndoe', icon: HiOutlineUser, type: 'text', required: true },
    { key: 'email', label: 'Email address', placeholder: 'you@company.com', icon: HiOutlineMail, type: 'email', required: true },
    { key: 'organization', label: 'Organization', placeholder: 'Acme Inc. (optional)', icon: HiOutlineOfficeBuilding, type: 'text', required: false },
    { key: 'password', label: 'Password', placeholder: '••••••••', icon: HiOutlineLockClosed, type: 'password', required: true },
  ];

  return (
    <div className="min-h-screen bg-dark-900 flex items-center justify-center p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-gradient-to-br from-teal to-brand-blue rounded-xl flex items-center justify-center">
            <HiOutlineSparkles className="text-dark-900 text-xl" />
          </div>
          <div>
            <p className="font-bold text-white">RecruitAI</p>
            <p className="text-xs text-gray-500">AI-Powered HRMS</p>
          </div>
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Create account</h1>
          <p className="text-gray-400">Start screening smarter with AI</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {fields.map(({ key, label, placeholder, icon: Icon, type, required }) => (
            <div key={key}>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                {label} {required && <span className="text-teal">*</span>}
              </label>
              <div className="relative">
                <Icon className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type={type} placeholder={placeholder} value={form[key]}
                  onChange={set(key)} className="input pl-10"
                  required={required}
                />
              </div>
            </div>
          ))}

          <motion.button
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={loading}
            className="btn-primary w-full justify-center py-3 text-base mt-2"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Creating account...
              </span>
            ) : 'Create account'}
          </motion.button>
        </form>

        <p className="text-center text-gray-500 text-sm mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-teal hover:underline font-medium">Sign in</Link>
        </p>
      </motion.div>
    </div>
  );
}
