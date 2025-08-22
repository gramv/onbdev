/**
 * Skip Navigation Component
 * 
 * WCAG 2.1 compliant skip navigation links for keyboard users
 * Provides quick access to main content areas bypassing repetitive navigation
 * 
 * Features:
 * - Visible only on focus (screen reader always accessible)
 * - High contrast styling for visibility
 * - Smooth scroll to target sections
 * - Multiple skip options for complex forms
 */

import React from 'react';
import { motion } from 'framer-motion';

interface SkipLink {
  href: string;
  label: string;
}

interface SkipNavigationProps {
  links?: SkipLink[];
  className?: string;
}

const defaultLinks: SkipLink[] = [
  { href: '#main-content', label: 'Skip to main content' },
  { href: '#form-navigation', label: 'Skip to form navigation' },
  { href: '#current-step', label: 'Skip to current step' },
];

export const SkipNavigation: React.FC<SkipNavigationProps> = ({
  links = defaultLinks,
  className = '',
}) => {
  const handleSkip = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault();
    const targetId = href.replace('#', '');
    const target = document.getElementById(targetId);
    
    if (target) {
      target.focus();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className={`skip-navigation ${className}`}>
      {links.map((link, index) => (
        <motion.a
          key={link.href}
          href={link.href}
          onClick={(e) => handleSkip(e, link.href)}
          className="skip-link"
          initial={{ opacity: 0, y: -20 }}
          whileFocus={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, delay: index * 0.05 }}
          style={{
            position: 'absolute',
            left: '-10000px',
            top: 'auto',
            width: '1px',
            height: '1px',
            overflow: 'hidden',
          }}
          onFocus={(e) => {
            e.currentTarget.style.position = 'fixed';
            e.currentTarget.style.left = '50%';
            e.currentTarget.style.transform = 'translateX(-50%)';
            e.currentTarget.style.top = '10px';
            e.currentTarget.style.width = 'auto';
            e.currentTarget.style.height = 'auto';
            e.currentTarget.style.overflow = 'visible';
            e.currentTarget.style.zIndex = '9999';
            e.currentTarget.style.padding = '12px 24px';
            e.currentTarget.style.backgroundColor = '#1a1a1a';
            e.currentTarget.style.color = '#ffffff';
            e.currentTarget.style.borderRadius = '8px';
            e.currentTarget.style.textDecoration = 'none';
            e.currentTarget.style.fontSize = '16px';
            e.currentTarget.style.fontWeight = '500';
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)';
          }}
          onBlur={(e) => {
            e.currentTarget.style.position = 'absolute';
            e.currentTarget.style.left = '-10000px';
            e.currentTarget.style.transform = 'none';
            e.currentTarget.style.top = 'auto';
            e.currentTarget.style.width = '1px';
            e.currentTarget.style.height = '1px';
            e.currentTarget.style.overflow = 'hidden';
            e.currentTarget.style.zIndex = 'auto';
            e.currentTarget.style.padding = '0';
          }}
        >
          {link.label}
        </motion.a>
      ))}
    </div>
  );
};

export default SkipNavigation;