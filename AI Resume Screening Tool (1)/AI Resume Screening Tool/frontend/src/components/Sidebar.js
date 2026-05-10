import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  HiOutlineViewGrid, HiOutlineBriefcase, HiOutlineUsers,
  HiOutlineChatAlt2, HiOutlineCog, HiOutlineChevronLeft,
  HiOutlineChevronRight, HiOutlineLogout, HiOutlineSparkles
} from 'react-icons/hi';
import useAuthStore from '../store/authStore';

const NAV = [
  { label: 'Dashboard',   path: '/dashboard',  icon: HiOutlineViewGrid },
  { label: 'Jobs',        path: '/jobs',        icon: HiOutlineBriefcase },
  { label: 'Candidates',  path: '/candidates',  icon: HiOutlineUsers },
  { label: 'AI Chat',     path: '/chat',        icon: HiOutlineChatAlt2 },
  { label: 'Settings',    path: '/settings',    icon: HiOutlineCog },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 240 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="relative flex flex-col bg-dark-800 border-r border-dark-500 h-screen flex-shrink-0 overflow-hidden"
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-dark-500 min-h-[72px]">
        <div className="w-9 h-9 bg-gradient-to-br from-teal to-brand-blue rounded-lg flex items-center justify-center flex-shrink-0">
          <HiOutlineSparkles className="text-dark-900 text-lg" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
            >
              <p className="font-bold text-white text-sm leading-tight">RecruitAI</p>
              <p className="text-xs text-gray-500">AI-Powered HRMS</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {!collapsed && <p className="text-xs text-gray-600 uppercase tracking-widest px-2 mb-3">Main Menu</p>}
        {NAV.map(({ label, path, icon: Icon }) => {
          const active = location.pathname.startsWith(path);
          return (
            <motion.button
              key={path}
              whileHover={{ x: 2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate(path)}
              className={`sidebar-link w-full ${active ? 'active' : ''} ${collapsed ? 'justify-center px-2' : ''}`}
              title={collapsed ? label : ''}
            >
              <Icon className="text-xl flex-shrink-0" />
              <AnimatePresence>
                {!collapsed && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.15 }}
                  >
                    {label}
                  </motion.span>
                )}
              </AnimatePresence>
            </motion.button>
          );
        })}
      </nav>

      {/* User + Logout */}
      <div className="px-3 pb-4 border-t border-dark-500 pt-3 space-y-1">
        {!collapsed && user && (
          <div className="px-3 py-2 mb-2">
            <p className="text-sm font-medium text-white truncate">{user.username || user.email}</p>
            <p className="text-xs text-gray-500 truncate">{user.email}</p>
          </div>
        )}
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={handleLogout}
          className={`sidebar-link w-full text-red-400 hover:text-red-300 hover:bg-red-500/10 ${collapsed ? 'justify-center px-2' : ''}`}
          title={collapsed ? 'Logout' : ''}
        >
          <HiOutlineLogout className="text-xl flex-shrink-0" />
          <AnimatePresence>
            {!collapsed && (
              <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                Logout
              </motion.span>
            )}
          </AnimatePresence>
        </motion.button>
      </div>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(c => !c)}
        className="absolute -right-3 top-20 w-6 h-6 bg-dark-600 border border-dark-500 rounded-full flex items-center justify-center text-gray-400 hover:text-teal hover:border-teal transition-all z-10"
      >
        {collapsed ? <HiOutlineChevronRight className="text-xs" /> : <HiOutlineChevronLeft className="text-xs" />}
      </button>
    </motion.aside>
  );
}
