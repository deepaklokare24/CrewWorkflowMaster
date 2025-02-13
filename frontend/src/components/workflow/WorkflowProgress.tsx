'use client'

import { useEffect, useState, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { format } from 'date-fns'
import { toast } from '@/components/ui/use-toast'

type WorkflowProgress = {
  id: string
  state: string
  current_step: string
  data: any
  created_at: string
  updated_at: string
  forms: Array<{
    id: string
    form_type: string
    submitted_by: string
    created_at: string
  }>
  approvals: Array<{
    id: string
    approver_id: string
    status: string
    decision: string
    comments: string
    created_at: string
  }>
  notifications: Array<{
    id: string
    recipient_id: string
    status: string
    created_at: string
    message?: string
  }>
}

type WorkflowProgressProps = {
  workflowId: string
}

export default function WorkflowProgress({ workflowId }: WorkflowProgressProps) {
  const [progress, setProgress] = useState<WorkflowProgress | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const handleWorkflowUpdate = useCallback((event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'initial_state' || data.type === 'workflow_update') {
        setProgress(prevProgress => ({
          ...prevProgress,
          ...data.data
        }))
        setLoading(false)

        // Show toast notification for updates
        if (data.type === 'workflow_update' && data.data.message) {
          toast({
            title: 'Workflow Update',
            description: data.data.message,
            duration: 5000
          })
        }
      }
    } catch (err) {
      console.error('Error processing workflow update:', err)
    }
  }, [])

  useEffect(() => {
    const eventSource = new EventSource(`/api/workflow/lease-exit/${workflowId}/events`)

    eventSource.onmessage = handleWorkflowUpdate
    
    eventSource.onerror = (err) => {
      console.error('EventSource error:', err)
      setError('Failed to connect to workflow updates. Please refresh the page.')
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [workflowId, handleWorkflowUpdate])

  const getStateColor = (state: string) => {
    const colors = {
      draft: 'bg-yellow-500',
      'in_progress': 'bg-blue-500',
      approved: 'bg-green-500',
      rejected: 'bg-red-500',
      completed: 'bg-purple-500'
    }
    return colors[state as keyof typeof colors] || 'bg-gray-500'
  }

  const getProgressPercentage = () => {
    const steps = [
      'initial',
      'advisory_review',
      'ifm_review',
      'mac_review',
      'pjm_review',
      'management_review',
      'approval_chain',
      'ready_for_exit',
      'completed'
    ]
    if (!progress) return 0
    const currentIndex = steps.indexOf(progress.current_step)
    return Math.round((currentIndex / (steps.length - 1)) * 100)
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            Loading workflow progress...
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-red-500">{error}</div>
        </CardContent>
      </Card>
    )
  }

  if (!progress) {
    return (
      <Card>
        <CardContent className="p-6">
          <div>No progress information available</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Workflow Progress</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Status</span>
            <Badge className={getStateColor(progress.state)}>
              {progress.state}
            </Badge>
          </div>
          <div className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Current Step</span>
              <span>{progress.current_step.replace('_', ' ').toUpperCase()}</span>
            </div>
            <Progress value={getProgressPercentage()} className="w-full" />
          </div>
        </div>

        <Separator />

        <div className="space-y-4">
          <h3 className="font-medium">Forms</h3>
          {progress.forms.length > 0 ? (
            <div className="space-y-2">
              {progress.forms.map(form => (
                <div key={form.id} className="flex justify-between text-sm">
                  <span>{form.form_type.replace('_', ' ').toUpperCase()}</span>
                  <span>{format(new Date(form.created_at), 'MMM d, yyyy')}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">No forms submitted yet</div>
          )}
        </div>

        <Separator />

        <div className="space-y-4">
          <h3 className="font-medium">Approvals</h3>
          {progress.approvals.length > 0 ? (
            <div className="space-y-2">
              {progress.approvals.map(approval => (
                <div key={approval.id} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>Approver {approval.approver_id}</span>
                    <Badge
                      className={
                        approval.decision === 'approved'
                          ? 'bg-green-500'
                          : approval.decision === 'rejected'
                          ? 'bg-red-500'
                          : 'bg-yellow-500'
                      }
                    >
                      {approval.status}
                    </Badge>
                  </div>
                  {approval.comments && (
                    <p className="text-sm text-muted-foreground">{approval.comments}</p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">No approvals yet</div>
          )}
        </div>

        <Separator />

        <div className="space-y-4">
          <h3 className="font-medium">Recent Activity</h3>
          {progress.notifications.length > 0 ? (
            <div className="space-y-2">
              {progress.notifications.map(notification => (
                <div key={notification.id} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>Notification to {notification.recipient_id}</span>
                    <span>
                      {format(new Date(notification.created_at), 'MMM d, yyyy')}
                    </span>
                  </div>
                  {notification.message && (
                    <p className="text-sm text-muted-foreground">{notification.message}</p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">No recent activity</div>
          )}
        </div>
      </CardContent>
    </Card>
  )
} 