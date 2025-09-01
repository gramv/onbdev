/**
 * Responsive PDF Viewer Component
 * Mobile-optimized PDF viewer with touch controls and responsive design
 */

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { 
  ZoomIn, 
  ZoomOut, 
  RotateCw, 
  Download, 
  Maximize2, 
  Minimize2,
  Loader2,
  AlertTriangle,
  RefreshCw
} from 'lucide-react'
import { cn } from '../lib/utils'
import { HealthInsuranceErrorDisplay } from './HealthInsuranceErrorDisplay'
import { healthInsuranceErrorHandler } from '../services/HealthInsuranceErrorHandler'
import { HealthInsuranceErrorType, ErrorSeverity } from '../types/healthInsuranceErrors'

interface ResponsivePDFViewerProps {
  pdfData: string
  title?: string
  onError?: (error: any) => void
  mobileOptimized?: boolean
  language?: 'en' | 'es'
  className?: string
  height?: string
  showControls?: boolean
  allowDownload?: boolean
}

interface PDFViewerState {
  loading: boolean
  error: any | null
  scale: number
  rotation: number
  isFullscreen: boolean
  retryCount: number
}

const useIsMobile = () => {
  const [isMobile, setIsMobile] = useState(false)
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])
  
  return isMobile
}

export function ResponsivePDFViewer({
  pdfData,
  title = 'Document Preview',
  onError,
  mobileOptimized = true,
  language = 'en',
  className = '',
  height,
  showControls = true,
  allowDownload = true
}: ResponsivePDFViewerProps) {
  const isMobile = useIsMobile()
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  
  const [viewerState, setViewerState] = useState<PDFViewerState>({
    loading: true,
    error: null,
    scale: isMobile ? 0.8 : 1.0,
    rotation: 0,
    isFullscreen: false,
    retryCount: 0
  })

  // Mobile-specific configuration
  const mobileConfig = {
    initialScale: 0.8,
    maxScale: 2.0,
    minScale: 0.5,
    scaleStep: 0.2,
    enablePinchZoom: true,
    showMobileControls: true
  }

  const desktopConfig = {
    initialScale: 1.0,
    maxScale: 3.0,
    minScale: 0.5,
    scaleStep: 0.25,
    enablePinchZoom: false,
    showMobileControls: false
  }

  const config = isMobile && mobileOptimized ? mobileConfig : desktopConfig

  // Calculate responsive height
  const getResponsiveHeight = useCallback(() => {
    if (height) return height
    
    if (isMobile) {
      return viewerState.isFullscreen ? '100vh' : '400px'
    } else {
      return viewerState.isFullscreen ? '100vh' : '600px'
    }
  }, [height, isMobile, viewerState.isFullscreen])

  // Handle PDF loading
  const handlePDFLoad = useCallback(() => {
    setViewerState(prev => ({ ...prev, loading: false, error: null }))
  }, [])

  // Handle PDF loading error
  const handlePDFError = useCallback((error: any) => {
    const healthError = healthInsuranceErrorHandler.createError(
      HealthInsuranceErrorType.PDF_DISPLAY_ERROR,
      'Failed to load PDF document',
      ErrorSeverity.MEDIUM,
      { pdfDataLength: pdfData?.length, title }
    )

    setViewerState(prev => ({ 
      ...prev, 
      loading: false, 
      error: healthError,
      retryCount: prev.retryCount + 1
    }))
    
    onError?.(healthError)
  }, [pdfData, title, onError])

  // Zoom controls
  const handleZoomIn = useCallback(() => {
    setViewerState(prev => ({
      ...prev,
      scale: Math.min(prev.scale + config.scaleStep, config.maxScale)
    }))
  }, [config])

  const handleZoomOut = useCallback(() => {
    setViewerState(prev => ({
      ...prev,
      scale: Math.max(prev.scale - config.scaleStep, config.minScale)
    }))
  }, [config])

  const handleFitToWidth = useCallback(() => {
    setViewerState(prev => ({ ...prev, scale: isMobile ? 0.8 : 1.0 }))
  }, [isMobile])

  const handleRotate = useCallback(() => {
    setViewerState(prev => ({ 
      ...prev, 
      rotation: (prev.rotation + 90) % 360 
    }))
  }, [])

  // Fullscreen toggle
  const handleFullscreenToggle = useCallback(() => {
    setViewerState(prev => ({ ...prev, isFullscreen: !prev.isFullscreen }))
  }, [])

  // Download PDF
  const handleDownload = useCallback(() => {
    try {
      const link = document.createElement('a')
      link.href = `data:application/pdf;base64,${pdfData}`
      link.download = `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (error) {
      const healthError = healthInsuranceErrorHandler.createError(
        HealthInsuranceErrorType.DOCUMENT_SAVE_ERROR,
        'Failed to download PDF',
        ErrorSeverity.LOW,
        { error }
      )
      onError?.(healthError)
    }
  }, [pdfData, title, onError])

  // Retry PDF loading
  const handleRetry = useCallback(() => {
    setViewerState(prev => ({ 
      ...prev, 
      loading: true, 
      error: null,
      scale: config.initialScale
    }))
    
    // Force iframe reload
    if (iframeRef.current) {
      iframeRef.current.src = `data:application/pdf;base64,${pdfData}#toolbar=0&navpanes=0&scrollbar=0`
    }
  }, [pdfData, config.initialScale])

  // Initialize PDF data
  useEffect(() => {
    if (pdfData && iframeRef.current) {
      const pdfUrl = `data:application/pdf;base64,${pdfData}#toolbar=0&navpanes=0&scrollbar=0`
      iframeRef.current.src = pdfUrl
    }
  }, [pdfData])

  // Handle error recovery
  const handleErrorAction = useCallback(async (action: string) => {
    switch (action) {
      case 'retry':
      case 'reload_pdf':
        handleRetry()
        break
      case 'download_pdf':
        handleDownload()
        break
      case 'skip_preview':
        // Emit skip event to parent
        onError?.({ type: 'skip_preview' })
        break
      default:
        console.warn('Unknown error action:', action)
    }
  }, [handleRetry, handleDownload, onError])

  if (!pdfData) {
    return (
      <Card className={cn("w-full", className)}>
        <CardContent className="p-6 text-center">
          <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">
            {language === 'es' ? 'No hay documento para mostrar' : 'No document to display'}
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className={cn(
      "relative w-full",
      viewerState.isFullscreen && "fixed inset-0 z-50 bg-white",
      className
    )}>
      {/* Mobile Controls */}
      {showControls && (isMobile || config.showMobileControls) && (
        <div className="flex items-center justify-between p-2 bg-gray-50 border-b">
          <div className="flex items-center gap-1">
            <Button
              variant="outline"
              size="sm"
              onClick={handleZoomOut}
              disabled={viewerState.scale <= config.minScale}
              className="h-8 w-8 p-0"
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            
            <span className="text-xs text-gray-600 min-w-[3rem] text-center">
              {Math.round(viewerState.scale * 100)}%
            </span>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleZoomIn}
              disabled={viewerState.scale >= config.maxScale}
              className="h-8 w-8 p-0"
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex items-center gap-1">
            <Button
              variant="outline"
              size="sm"
              onClick={handleFitToWidth}
              className="h-8 px-2"
            >
              <span className="text-xs">
                {language === 'es' ? 'Ajustar' : 'Fit'}
              </span>
            </Button>
            
            {allowDownload && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleDownload}
                className="h-8 w-8 p-0"
              >
                <Download className="h-4 w-4" />
              </Button>
            )}
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleFullscreenToggle}
              className="h-8 w-8 p-0"
            >
              {viewerState.isFullscreen ? (
                <Minimize2 className="h-4 w-4" />
              ) : (
                <Maximize2 className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      )}

      {/* PDF Display Container */}
      <div 
        ref={containerRef}
        className="relative overflow-hidden bg-gray-100"
        style={{ height: getResponsiveHeight() }}
      >
        {/* Loading State */}
        {viewerState.loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-2" />
              <p className="text-gray-600 text-sm">
                {language === 'es' ? 'Cargando documento...' : 'Loading document...'}
              </p>
            </div>
          </div>
        )}

        {/* Error State */}
        {viewerState.error && (
          <div className="absolute inset-0 z-10">
            <HealthInsuranceErrorDisplay
              error={viewerState.error}
              language={language}
              onAction={handleErrorAction}
              className="h-full flex items-center justify-center"
            />
          </div>
        )}

        {/* PDF Iframe */}
        <iframe
          ref={iframeRef}
          className={cn(
            "w-full h-full border-0 transition-transform duration-200",
            viewerState.loading && "opacity-0",
            viewerState.error && "hidden"
          )}
          style={{
            transform: `scale(${viewerState.scale}) rotate(${viewerState.rotation}deg)`,
            transformOrigin: 'top left'
          }}
          title={title}
          onLoad={handlePDFLoad}
          onError={handlePDFError}
        />
      </div>

      {/* Desktop Controls */}
      {showControls && !isMobile && !config.showMobileControls && (
        <div className="flex items-center justify-between p-3 bg-gray-50 border-t">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleZoomOut}
              disabled={viewerState.scale <= config.minScale}
            >
              <ZoomOut className="h-4 w-4 mr-1" />
              {language === 'es' ? 'Alejar' : 'Zoom Out'}
            </Button>
            
            <span className="text-sm text-gray-600 min-w-[4rem] text-center">
              {Math.round(viewerState.scale * 100)}%
            </span>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleZoomIn}
              disabled={viewerState.scale >= config.maxScale}
            >
              <ZoomIn className="h-4 w-4 mr-1" />
              {language === 'es' ? 'Acercar' : 'Zoom In'}
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleFitToWidth}
            >
              {language === 'es' ? 'Ajustar al Ancho' : 'Fit to Width'}
            </Button>
          </div>

          <div className="flex items-center gap-2">
            {allowDownload && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleDownload}
              >
                <Download className="h-4 w-4 mr-1" />
                {language === 'es' ? 'Descargar' : 'Download'}
              </Button>
            )}
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleFullscreenToggle}
            >
              {viewerState.isFullscreen ? (
                <>
                  <Minimize2 className="h-4 w-4 mr-1" />
                  {language === 'es' ? 'Salir' : 'Exit'}
                </>
              ) : (
                <>
                  <Maximize2 className="h-4 w-4 mr-1" />
                  {language === 'es' ? 'Pantalla Completa' : 'Fullscreen'}
                </>
              )}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
