import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiOutlineSearch, HiOutlineBell, HiOutlineSparkles } from 'react-icons/hi';
import useAuthStore from '../store/authStore';

export default function Topbar({ title, subtitle }) {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-dark-500 bg-dark-900/80 backdrop-blur-sm sticky top-0 z-10">
      <div>
        <motion.h1
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-xl font-bold text-white"
        >
          {title}
        </motion.h1>
        {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="relative hidden md:flex items-center">
          <HiOutlineSearch className="absolute left-3 text-gray-500 text-sm" />
          <input
            type="text"
            placeholder="Search candidates, jobs..."
            className="input pl-9 w-56 py-2 text-sm"
          />
        </div>

        {/* Notification */}
        <motion.button
          whileTap={{ scale: 0.95 }}
          className="relative w-9 h-9 bg-dark-700 border border-dark-500 rounded-lg flex items-center justify-center text-gray-400 hover:text-teal hover:border-teal transition-all"
        >
          <HiOutlineBell className="text-lg" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-teal rounded-full" />
        </motion.button>

        {/* Avatar */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="w-9 h-9 bg-gradient-to-br from-teal to-brand-blue rounded-lg flex items-center justify-center cursor-pointer"
          onClick={() => navigate('/settings')}
          title={user?.username}
        >
          <span className="text-dark-900 font-bold text-sm">
            {(user?.username || user?.email || 'U')[0].toUpperCase()}
          </span>
        </motion.div>
      </div>
    </header>
  );
}
