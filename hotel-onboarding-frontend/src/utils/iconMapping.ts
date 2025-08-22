/**
 * Icon Mapping Utility
 * 
 * Maps form sections and fields to appropriate Lucide React icons
 * Provides consistent iconography throughout the application
 * 
 * Icons chosen for clarity and professional appearance
 */

import {
  // Form Section Icons
  User,
  Briefcase,
  Building2,
  GraduationCap,
  FileText,
  CheckCircle2,
  Shield,
  
  // Field Icons
  Mail,
  Phone,
  MapPin,
  Calendar,
  CreditCard,
  Globe,
  Hash,
  
  // Action Icons
  Upload,
  Download,
  Save,
  Send,
  Search,
  Filter,
  Edit,
  Trash2,
  Plus,
  Minus,
  X,
  Check,
  
  // Status Icons
  AlertCircle,
  Info,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  
  // Navigation Icons
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  ArrowLeft,
  ArrowRight,
  
  // Utility Icons
  Eye,
  EyeOff,
  Copy,
  Clipboard,
  Lock,
  Unlock,
  Settings,
  HelpCircle,
  MoreVertical,
  MoreHorizontal,
  
  // Document Icons
  File,
  FileCheck,
  FilePlus,
  FileX,
  Paperclip,
  
  // Communication Icons
  MessageSquare,
  Bell,
  BellOff,
  
  // Data Icons
  Database,
  HardDrive,
  Cloud,
  CloudUpload,
  CloudDownload,
  
  // User Management Icons
  UserPlus,
  UserMinus,
  UserCheck,
  UserX,
  Users,
  
  // Form Specific Icons
  ClipboardList,
  ListChecks,
  FormInput,
  
  // Additional Professional Icons
  Award,
  Badge,
  Star,
  Flag,
  Target,
  TrendingUp,
  BarChart,
  PieChart,
  
  LucideIcon,
} from 'lucide-react';

/**
 * Form Section Icons
 * Main sections of the job application form
 */
export const formSectionIcons: Record<string, LucideIcon> = {
  // Primary Form Sections
  personalInfo: User,
  position: Briefcase,
  employment: Building2,
  education: GraduationCap,
  additional: FileText,
  review: CheckCircle2,
  selfIdentification: Shield,
  
  // Additional Sections
  contact: Phone,
  address: MapPin,
  emergencyContact: AlertCircle,
  references: Users,
  documents: Paperclip,
  availability: Calendar,
  skills: Award,
  certifications: Badge,
  languages: Globe,
  
  // Onboarding Sections
  taxInformation: CreditCard,
  directDeposit: Building2,
  beneficiaries: Users,
  policies: ClipboardList,
  training: GraduationCap,
  equipment: Briefcase,
  
  // Compliance Sections
  i9Verification: Shield,
  w4Form: FileText,
  stateWithholding: MapPin,
  backgroundCheck: Search,
  drugTest: FileCheck,
};

/**
 * Field Type Icons
 * Icons for specific input field types
 */
export const fieldTypeIcons: Record<string, LucideIcon> = {
  email: Mail,
  phone: Phone,
  address: MapPin,
  date: Calendar,
  ssn: Hash,
  ein: Building2,
  accountNumber: CreditCard,
  routingNumber: Building2,
  website: Globe,
  search: Search,
  password: Lock,
  file: Upload,
  signature: Edit,
  checkbox: CheckCircle2,
  radio: CheckCircle,
};

/**
 * Action Icons
 * Icons for form actions and buttons
 */
export const actionIcons: Record<string, LucideIcon> = {
  submit: Send,
  save: Save,
  saveDraft: FileText,
  cancel: X,
  delete: Trash2,
  edit: Edit,
  add: Plus,
  remove: Minus,
  upload: Upload,
  download: Download,
  search: Search,
  filter: Filter,
  copy: Copy,
  paste: Clipboard,
  clear: X,
  reset: ArrowLeft,
  next: ChevronRight,
  previous: ChevronLeft,
  finish: CheckCircle2,
  help: HelpCircle,
  settings: Settings,
  more: MoreVertical,
  view: Eye,
  hide: EyeOff,
};

/**
 * Status Icons
 * Icons for different states and statuses
 */
export const statusIcons: Record<string, LucideIcon> = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
  pending: Clock,
  inProgress: Clock,
  completed: CheckCircle2,
  rejected: XCircle,
  approved: CheckCircle,
  draft: FileText,
  submitted: Send,
  reviewing: Eye,
  verified: Shield,
  unverified: AlertCircle,
  locked: Lock,
  unlocked: Unlock,
  required: AlertCircle,
  optional: Info,
};

/**
 * Document Type Icons
 * Icons for different document types
 */
export const documentTypeIcons: Record<string, LucideIcon> = {
  pdf: File,
  image: FileText,
  resume: FileText,
  coverLetter: FileText,
  certificate: Award,
  license: Badge,
  passport: Shield,
  driversLicense: CreditCard,
  socialSecurity: Hash,
  i9: Shield,
  w4: FileText,
  contract: ClipboardList,
  policy: ClipboardList,
  handbook: FileText,
  training: GraduationCap,
};

/**
 * Navigation Icons
 * Icons for navigation elements
 */
export const navigationIcons: Record<string, LucideIcon> = {
  back: ArrowLeft,
  forward: ArrowRight,
  up: ChevronUp,
  down: ChevronDown,
  left: ChevronLeft,
  right: ChevronRight,
  home: Building2,
  menu: MoreHorizontal,
  close: X,
};

/**
 * Helper function to get icon by category and name
 */
export const getIcon = (category: string, name: string): LucideIcon | undefined => {
  const categories: Record<string, Record<string, LucideIcon>> = {
    section: formSectionIcons,
    field: fieldTypeIcons,
    action: actionIcons,
    status: statusIcons,
    document: documentTypeIcons,
    navigation: navigationIcons,
  };
  
  return categories[category]?.[name];
};

/**
 * Get icon with default fallback
 */
export const getIconWithFallback = (
  category: string, 
  name: string, 
  fallback: LucideIcon = FileText
): LucideIcon => {
  return getIcon(category, name) || fallback;
};

/**
 * Icon configuration for consistent sizing and styling
 */
export const iconConfig = {
  sizes: {
    xs: 12,
    sm: 16,
    md: 20,
    lg: 24,
    xl: 32,
    '2xl': 40,
  },
  
  defaultProps: {
    size: 20,
    strokeWidth: 1.5,
  },
  
  sectionIconProps: {
    size: 24,
    strokeWidth: 1.5,
    className: 'text-primary-600',
  },
  
  fieldIconProps: {
    size: 20,
    strokeWidth: 1.5,
    className: 'text-neutral-500',
  },
  
  actionIconProps: {
    size: 18,
    strokeWidth: 2,
    className: 'text-current',
  },
  
  statusIconProps: {
    size: 16,
    strokeWidth: 2,
    className: 'text-current',
  },
};

/**
 * Get form step icon and label
 */
export interface FormStep {
  id: string;
  label: string;
  icon: LucideIcon;
  description?: string;
}

export const formSteps: FormStep[] = [
  {
    id: 'personal',
    label: 'Personal Information',
    icon: User,
    description: 'Basic details about yourself',
  },
  {
    id: 'position',
    label: 'Position & Availability',
    icon: Briefcase,
    description: 'Job preferences and schedule',
  },
  {
    id: 'employment',
    label: 'Employment History',
    icon: Building2,
    description: 'Previous work experience',
  },
  {
    id: 'education',
    label: 'Education',
    icon: GraduationCap,
    description: 'Educational background',
  },
  {
    id: 'additional',
    label: 'Additional Information',
    icon: FileText,
    description: 'References and other details',
  },
  {
    id: 'selfId',
    label: 'Self-Identification',
    icon: Shield,
    description: 'Optional demographic information',
  },
  {
    id: 'review',
    label: 'Review & Submit',
    icon: CheckCircle2,
    description: 'Review and submit your application',
  },
];

/**
 * Get appropriate icon color class based on status
 */
export const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    success: 'text-success-600',
    completed: 'text-success-600',
    approved: 'text-success-600',
    verified: 'text-success-600',
    
    error: 'text-error-600',
    rejected: 'text-error-600',
    failed: 'text-error-600',
    
    warning: 'text-warning-600',
    pending: 'text-warning-600',
    inProgress: 'text-warning-600',
    
    info: 'text-info-600',
    draft: 'text-neutral-500',
    optional: 'text-neutral-400',
    
    default: 'text-neutral-600',
  };
  
  return colorMap[status] || colorMap.default;
};

/**
 * Validation state icons
 */
export const validationIcons = {
  valid: CheckCircle,
  invalid: XCircle,
  warning: AlertTriangle,
  info: Info,
  required: AlertCircle,
};

/**
 * File type icons based on extension
 */
export const getFileTypeIcon = (filename: string): LucideIcon => {
  const extension = filename.split('.').pop()?.toLowerCase();
  
  const fileTypeMap: Record<string, LucideIcon> = {
    pdf: File,
    doc: FileText,
    docx: FileText,
    txt: FileText,
    png: FileText,
    jpg: FileText,
    jpeg: FileText,
    gif: FileText,
    zip: File,
    default: Paperclip,
  };
  
  return fileTypeMap[extension || ''] || fileTypeMap.default;
};

// Export all icon collections for easy access
export default {
  formSectionIcons,
  fieldTypeIcons,
  actionIcons,
  statusIcons,
  documentTypeIcons,
  navigationIcons,
  getIcon,
  getIconWithFallback,
  iconConfig,
  formSteps,
  getStatusColor,
  validationIcons,
  getFileTypeIcon,
};