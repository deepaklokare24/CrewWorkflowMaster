"use client"

import { useEffect, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/components/ui/use-toast"

type WorkflowProgress = {
  current_step: string
  total_steps: number
  completed_steps: number
  forms: string[]
  message?: string
}

type WorkflowProgressProps = {
  workflowId: string
}

export function WorkflowProgress({ workflowId }: WorkflowProgressProps) {
  const [progress, setProgress] = useState<WorkflowProgress | null>(null)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    const eventSource = new EventSource(`/api/workflow/lease-exit/${workflowId}/events`)

    const handleWorkflowUpdate = (event: MessageEvent) => {
      const data = JSON.parse(event.data)
      if (data.type === "workflow_update") {
        setProgress(data.progress)
        if (data.progress.message) {
          toast({
            title: "Workflow Update",
            description: data.progress.message,
          })
        }
      }
    }

    eventSource.onmessage = handleWorkflowUpdate
    eventSource.onerror = (error) => {
      console.error("EventSource failed:", error)
      setError("Failed to connect to event stream")
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [workflowId, toast])

  if (error) {
    return <div className="text-red-500">{error}</div>
  }

  if (!progress) {
    return <div>Loading workflow progress...</div>
  }

  const progressPercentage = (progress.completed_steps / progress.total_steps) * 100

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Current Progress</h3>
        <p className="text-sm text-muted-foreground">
          Step {progress.completed_steps} of {progress.total_steps}
        </p>
      </div>

      <Progress value={progressPercentage} />

      <div>
        <h4 className="text-sm font-medium mb-2">Current Step</h4>
        <Badge variant="outline">
          {progress.current_step.replace(/_/g, " ")}
        </Badge>
      </div>

      {progress.forms.length > 0 && (
        <>
          <Separator />
          <div>
            <h4 className="text-sm font-medium mb-2">Required Forms</h4>
            <div className="space-y-2">
              {progress.forms.map((form, index) => (
                <Badge key={index} variant="secondary">
                  {form.replace(/_/g, " ")}
                </Badge>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
} 