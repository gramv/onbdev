/**
 * Mobile-Optimized Signature Capture Component
 * Touch-friendly signature capture with high DPI support and mobile optimizations
 */

import React, { useRef, useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Pen, 
  Eraser, 
  RotateCcw, 
  Check, 
  X, 
  Smartphone,
  Monitor,
  AlertTriangle
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { SignatureData } from '../types/healthInsuranceState'

interface Point {
  x: number
  y: number
  pressure?: number
  timestamp?: number
}

interface MobileSignatureCaptureProps {
  onSignature: (signature: SignatureData) => void
  onCancel: () => void
  language?: 'en' | 'es'
  className?: string
  required?: boolean
  title?: string
  instructions?: string
}

interface SignatureState {
  isDrawing: boolean
  points: Point[]
  isEmpty: boolean
  canvasReady: boolean
  error: string | null
}

const useIsMobile = () => {
  const [isMobile, setIsMobile] = useState(false)
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768 || 'ontouchstart' in window)
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])
  
  return isMobile
}

export function MobileSignatureCapture({
  onSignature,
  onCancel,
  language = 'en',
  className = '',
  required = true,
  title,
  instructions
}: MobileSignatureCaptureProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const isMobile = useIsMobile()
  
  const [signatureState, setSignatureState] = useState<SignatureState>({
    isDrawing: false,
    points: [],
    isEmpty: true,
    canvasReady: false,
    error: null
  })

  // Get default title and instructions based on language
  const getTitle = () => {
    if (title) return title
    return language === 'es' ? 'Firma Digital' : 'Digital Signature'
  }

  const getInstructions = () => {
    if (instructions) return instructions
    
    if (isMobile) {
      return language === 'es' 
        ? 'Use su dedo para firmar en el recuadro de abajo. Asegúrese de que su firma sea clara y legible.'
        : 'Use your finger to sign in the box below. Make sure your signature is clear and legible.'
    } else {
      return language === 'es'
        ? 'Use su mouse o trackpad para firmar en el recuadro de abajo.'
        : 'Use your mouse or trackpad to sign in the box below.'
    }
  }

  // Initialize canvas with high DPI support
  const initializeCanvas = useCallback(() => {
    const canvas = canvasRef.current
    const container = containerRef.current
    if (!canvas || !container) return

    try {
      // Get device pixel ratio for high DPI displays
      const dpr = window.devicePixelRatio || 1
      const rect = container.getBoundingClientRect()
      
      // Set canvas size with DPI scaling
      canvas.width = rect.width * dpr
      canvas.height = (isMobile ? 150 : 200) * dpr
      
      // Scale canvas back down using CSS
      canvas.style.width = `${rect.width}px`
      canvas.style.height = `${isMobile ? 150 : 200}px`
      
      const ctx = canvas.getContext('2d')
      if (ctx) {
        // Scale context to match DPI
        ctx.scale(dpr, dpr)
        
        // Set drawing properties
        ctx.strokeStyle = '#000000'
        ctx.lineWidth = isMobile ? 3 : 2
        ctx.lineCap = 'round'
        ctx.lineJoin = 'round'
        ctx.imageSmoothingEnabled = true
        
        // Clear canvas with white background
        ctx.fillStyle = '#ffffff'
        ctx.fillRect(0, 0, canvas.width / dpr, canvas.height / dpr)
        
        setSignatureState(prev => ({ ...prev, canvasReady: true, error: null }))
      }
    } catch (error) {
      setSignatureState(prev => ({ 
        ...prev, 
        error: language === 'es' 
          ? 'Error al inicializar el lienzo de firma'
          : 'Failed to initialize signature canvas'
      }))
    }
  }, [isMobile, language])

  // Get coordinates from touch/mouse event
  const getEventCoordinates = useCallback((e: TouchEvent | MouseEvent): Point | null => {
    const canvas = canvasRef.current
    if (!canvas) return null

    const rect = canvas.getBoundingClientRect()
    let clientX: number, clientY: number, pressure = 1

    if ('touches' in e) {
      // Touch event
      if (e.touches.length === 0) return null
      const touch = e.touches[0]
      clientX = touch.clientX
      clientY = touch.clientY
      
      // Try to get pressure from touch (if supported)
      if ('force' in touch && touch.force > 0) {
        pressure = touch.force
      }
    } else {
      // Mouse event
      clientX = e.clientX
      clientY = e.clientY
      
      // Try to get pressure from pointer event (if supported)
      if ('pressure' in e && typeof e.pressure === 'number') {
        pressure = e.pressure
      }
    }

    return {
      x: clientX - rect.left,
      y: clientY - rect.top,
      pressure,
      timestamp: Date.now()
    }
  }, [])

  // Start drawing
  const startDrawing = useCallback((e: TouchEvent | MouseEvent) => {
    e.preventDefault()
    
    const point = getEventCoordinates(e)
    if (!point) return

    const canvas = canvasRef.current
    const ctx = canvas?.getContext('2d')
    if (!ctx) return

    setSignatureState(prev => ({ 
      ...prev, 
      isDrawing: true, 
      points: [point],
      isEmpty: false
    }))

    ctx.beginPath()
    ctx.moveTo(point.x, point.y)
  }, [getEventCoordinates])

  // Continue drawing
  const continueDrawing = useCallback((e: TouchEvent | MouseEvent) => {
    e.preventDefault()
    
    if (!signatureState.isDrawing) return

    const point = getEventCoordinates(e)
    if (!point) return

    const canvas = canvasRef.current
    const ctx = canvas?.getContext('2d')
    if (!ctx) return

    setSignatureState(prev => ({ 
      ...prev, 
      points: [...prev.points, point]
    }))

    // Adjust line width based on pressure (if available)
    if (point.pressure && point.pressure > 0) {
      ctx.lineWidth = (isMobile ? 3 : 2) * Math.max(0.5, point.pressure)
    }

    ctx.lineTo(point.x, point.y)
    ctx.stroke()
  }, [signatureState.isDrawing, getEventCoordinates, isMobile])

  // Stop drawing
  const stopDrawing = useCallback(() => {
    setSignatureState(prev => ({ ...prev, isDrawing: false }))
  }, [])

  // Clear signature
  const clearSignature = useCallback(() => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext('2d')
    if (!ctx || !canvas) return

    // Clear canvas and redraw background
    const dpr = window.devicePixelRatio || 1
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width / dpr, canvas.height / dpr)

    setSignatureState(prev => ({ 
      ...prev, 
      points: [], 
      isEmpty: true,
      error: null
    }))
  }, [])

  // Accept signature
  const acceptSignature = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas || signatureState.isEmpty) return

    try {
      // Convert canvas to base64
      const signatureDataUrl = canvas.toDataURL('image/png', 1.0)
      
      // Create signature data object
      const signature: SignatureData = {
        signature: signatureDataUrl,
        signedDate: new Date().toISOString(),
        ipAddress: undefined, // Would be set by backend
        userAgent: navigator.userAgent,
        coordinates: {
          x: 0,
          y: 0,
          width: canvas.width,
          height: canvas.height
        }
      }

      onSignature(signature)
    } catch (error) {
      setSignatureState(prev => ({ 
        ...prev, 
        error: language === 'es' 
          ? 'Error al procesar la firma'
          : 'Failed to process signature'
      }))
    }
  }, [signatureState.isEmpty, onSignature, language])

  // Set up event listeners
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !signatureState.canvasReady) return

    // Touch events for mobile
    const handleTouchStart = (e: TouchEvent) => startDrawing(e)
    const handleTouchMove = (e: TouchEvent) => continueDrawing(e)
    const handleTouchEnd = () => stopDrawing()

    // Mouse events for desktop
    const handleMouseDown = (e: MouseEvent) => startDrawing(e)
    const handleMouseMove = (e: MouseEvent) => continueDrawing(e)
    const handleMouseUp = () => stopDrawing()

    if (isMobile) {
      canvas.addEventListener('touchstart', handleTouchStart, { passive: false })
      canvas.addEventListener('touchmove', handleTouchMove, { passive: false })
      canvas.addEventListener('touchend', handleTouchEnd)
      canvas.addEventListener('touchcancel', handleTouchEnd)
    } else {
      canvas.addEventListener('mousedown', handleMouseDown)
      canvas.addEventListener('mousemove', handleMouseMove)
      canvas.addEventListener('mouseup', handleMouseUp)
      canvas.addEventListener('mouseleave', handleMouseUp)
    }

    return () => {
      if (isMobile) {
        canvas.removeEventListener('touchstart', handleTouchStart)
        canvas.removeEventListener('touchmove', handleTouchMove)
        canvas.removeEventListener('touchend', handleTouchEnd)
        canvas.removeEventListener('touchcancel', handleTouchEnd)
      } else {
        canvas.removeEventListener('mousedown', handleMouseDown)
        canvas.removeEventListener('mousemove', handleMouseMove)
        canvas.removeEventListener('mouseup', handleMouseUp)
        canvas.removeEventListener('mouseleave', handleMouseUp)
      }
    }
  }, [signatureState.canvasReady, isMobile, startDrawing, continueDrawing, stopDrawing])

  // Initialize canvas on mount and resize
  useEffect(() => {
    initializeCanvas()
    
    const handleResize = () => {
      setTimeout(initializeCanvas, 100) // Delay to ensure container has new size
    }
    
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [initializeCanvas])

  return (
    <Card className={cn("w-full max-w-2xl mx-auto", className)}>
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          {isMobile ? <Smartphone className="h-5 w-5" /> : <Monitor className="h-5 w-5" />}
          {getTitle()}
          {required && <span className="text-red-500">*</span>}
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Instructions */}
        <Alert>
          <Pen className="h-4 w-4" />
          <AlertDescription>
            {getInstructions()}
          </AlertDescription>
        </Alert>

        {/* Error Display */}
        {signatureState.error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              {signatureState.error}
            </AlertDescription>
          </Alert>
        )}

        {/* Signature Canvas Container */}
        <div 
          ref={containerRef}
          className="relative w-full border-2 border-dashed border-gray-300 rounded-lg bg-white overflow-hidden"
        >
          <canvas
            ref={canvasRef}
            className={cn(
              "block w-full cursor-crosshair touch-none",
              signatureState.isDrawing && "cursor-none",
              !signatureState.canvasReady && "opacity-50"
            )}
            style={{ 
              touchAction: 'none',
              height: isMobile ? '150px' : '200px'
            }}
          />
          
          {/* Empty state overlay */}
          {signatureState.isEmpty && signatureState.canvasReady && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <p className="text-gray-400 text-sm text-center px-4">
                {language === 'es' 
                  ? 'Toque aquí para firmar'
                  : 'Tap here to sign'
                }
              </p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-between">
          <Button
            variant="outline"
            onClick={clearSignature}
            disabled={signatureState.isEmpty}
            className="flex items-center gap-2"
          >
            <RotateCcw className="h-4 w-4" />
            {language === 'es' ? 'Limpiar' : 'Clear'}
          </Button>
          
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={onCancel}
              className="flex items-center gap-2"
            >
              <X className="h-4 w-4" />
              {language === 'es' ? 'Cancelar' : 'Cancel'}
            </Button>
            
            <Button
              onClick={acceptSignature}
              disabled={signatureState.isEmpty}
              className="flex items-center gap-2"
            >
              <Check className="h-4 w-4" />
              {language === 'es' ? 'Aceptar Firma' : 'Accept Signature'}
            </Button>
          </div>
        </div>

        {/* Signature Info */}
        {!signatureState.isEmpty && (
          <div className="text-xs text-gray-500 text-center">
            {language === 'es' 
              ? `Puntos capturados: ${signatureState.points.length}`
              : `Points captured: ${signatureState.points.length}`
            }
          </div>
        )}
      </CardContent>
    </Card>
  )
}
