"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { ArrowLeft, Plus, X, Upload, Brain, Loader2, FileText } from "lucide-react"
import { API_ENDPOINTS } from "@/lib/config"

export default function AddCasePage({ params }: { params: { user_id: string } }) {
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    chief_complaint: "",
    previous_medical_history: "",
    imageological_examination: "",
    laboratory_examination: "",
    pathological_examination: "",
  })
  const [differentialDiagnosis, setDifferentialDiagnosis] = useState<string[]>([])
  const [newDiagnosis, setNewDiagnosis] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isDiagnosing, setIsDiagnosing] = useState(false)
  const [error, setError] = useState("")
  const [diagnosisResult, setDiagnosisResult] = useState<{
    case_id: number
    final_diagnosis: string
    reasoning: string
  } | null>(null)

  const router = useRouter()
  const { user_id } = params

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const addDifferentialDiagnosis = () => {
    if (newDiagnosis.trim() && !differentialDiagnosis.includes(newDiagnosis.trim())) {
      setDifferentialDiagnosis((prev) => [...prev, newDiagnosis.trim()])
      setNewDiagnosis("")
    }
  }

  const removeDifferentialDiagnosis = (index: number) => {
    setDifferentialDiagnosis((prev) => prev.filter((_, i) => i !== index))
  }

  const handlePdfUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsLoading(true)
    setError("")

    const formDataUpload = new FormData()
    formDataUpload.append("file", file) // Changed from "pdf" to "file" to match backend

    try {
      const response = await fetch(API_ENDPOINTS.UPLOAD_PDF, {
        method: "POST",
        body: formDataUpload,
        // Don't set Content-Type header - let browser set it for FormData
      })

      if (response.ok) {
        const data = await response.json()
        console.log("PDF upload response:", data) // For debugging
        
        // For now, just show success message since backend doesn't extract data yet
        // In the future, when you implement PDF text extraction, you can populate the form
        alert(`PDF uploaded successfully: ${data.filename}`)
        
        // TODO: When you implement PDF text extraction, uncomment this:
        // setFormData({
        //   name: data.extracted_data?.name || "",
        //   age: data.extracted_data?.age?.toString() || "",
        //   chief_complaint: data.extracted_data?.chief_complaint || "",
        //   previous_medical_history: data.extracted_data?.previous_medical_history || "",
        //   imageological_examination: data.extracted_data?.imageological_examination || "",
        //   laboratory_examination: data.extracted_data?.laboratory_examination || "",
        //   pathological_examination: data.extracted_data?.pathological_examination || "",
        // })
      } else {
        const errorData = await response.json().catch(() => ({}))
        setError(`Failed to process PDF file: ${errorData.detail || response.statusText}`)
      }
    } catch (err) {
      console.error("PDF upload error:", err)
      setError("Error uploading PDF file")
    } finally {
      setIsLoading(false)
    }
  }

  const findDiagnosis = async () => {
    if (!formData.name || !formData.age || !formData.chief_complaint) {
      setError("Please fill in at least name, age, and chief complaint")
      return
    }

    setIsDiagnosing(true)
    setError("")

    try {
      const response = await fetch(API_ENDPOINTS.CASE(), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id,
          ...formData,
          age: Number.parseInt(formData.age),
          differential_diagnosis: differentialDiagnosis,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setDiagnosisResult({
          case_id: data.case_id,
          final_diagnosis: data.final_diagnosis,
          reasoning: data.reasoning,
        })
      } else {
        setError("Failed to find diagnosis")
      }
    } catch (err) {
      setError("Error finding diagnosis")
    } finally {
      setIsDiagnosing(false)
    }
  }

  const handleBack = () => {
    router.push(`/cases/${user_id}`)
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Button
            onClick={handleBack}
            variant="outline"
            className="border-green-500 text-green-500 hover:bg-green-500 hover:text-black bg-transparent"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Cases
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-green-500">Add New Case</h1>
            <p className="text-gray-400">Create a new medical case</p>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* PDF Upload */}
          <Card className="bg-gray-900 border-gray-700 lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-green-500 flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Upload Case PDF
              </CardTitle>
              <CardDescription className="text-gray-400">
                Upload a PDF file to automatically extract case information
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4">
                <Input
                  type="file"
                  accept=".pdf"
                  onChange={handlePdfUpload}
                  className="bg-gray-800 border-gray-600 text-white file:bg-green-600 file:text-white file:border-0 file:rounded file:px-4 file:py-2"
                  disabled={isLoading}
                />
                {isLoading && <Loader2 className="h-4 w-4 animate-spin text-green-500" />}
              </div>
            </CardContent>
          </Card>

          {/* Patient Information */}
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-green-500">Patient Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="name" className="text-white">
                  Name *
                </Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleInputChange("name", e.target.value)}
                  className="bg-gray-800 border-gray-600 text-white"
                  required
                />
              </div>
              <div>
                <Label htmlFor="age" className="text-white">
                  Age *
                </Label>
                <Input
                  id="age"
                  type="number"
                  value={formData.age}
                  onChange={(e) => handleInputChange("age", e.target.value)}
                  className="bg-gray-800 border-gray-600 text-white"
                  required
                />
              </div>
              <div>
                <Label htmlFor="chief_complaint" className="text-white">
                  Chief Complaint *
                </Label>
                <Textarea
                  id="chief_complaint"
                  value={formData.chief_complaint}
                  onChange={(e) => handleInputChange("chief_complaint", e.target.value)}
                  className="bg-gray-800 border-gray-600 text-white"
                  rows={3}
                  required
                />
              </div>
            </CardContent>
          </Card>

          {/* Medical History */}
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-green-500">Medical History</CardTitle>
            </CardHeader>
            <CardContent>
              <div>
                <Label htmlFor="previous_medical_history" className="text-white">
                  Previous Medical History
                </Label>
                <Textarea
                  id="previous_medical_history"
                  value={formData.previous_medical_history}
                  onChange={(e) => handleInputChange("previous_medical_history", e.target.value)}
                  className="bg-gray-800 border-gray-600 text-white"
                  rows={4}
                />
              </div>
            </CardContent>
          </Card>

          {/* Examinations */}
          <Card className="bg-gray-900 border-gray-700 lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-green-500">Examinations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="imageological_examination" className="text-white">
                  Imageological Examination
                </Label>
                <Textarea
                  id="imageological_examination"
                  value={formData.imageological_examination}
                  onChange={(e) => handleInputChange("imageological_examination", e.target.value)}
                  className="bg-gray-800 border-gray-600 text-white"
                  rows={3}
                />
              </div>
              <div>
                <Label htmlFor="laboratory_examination" className="text-white">
                  Laboratory Examination
                </Label>
                <Textarea
                  id="laboratory_examination"
                  value={formData.laboratory_examination}
                  onChange={(e) => handleInputChange("laboratory_examination", e.target.value)}
                  className="bg-gray-800 border-gray-600 text-white"
                  rows={3}
                />
              </div>
              <div>
                <Label htmlFor="pathological_examination" className="text-white">
                  Pathological Examination
                </Label>
                <Textarea
                  id="pathological_examination"
                  value={formData.pathological_examination}
                  onChange={(e) => handleInputChange("pathological_examination", e.target.value)}
                  className="bg-gray-800 border-gray-600 text-white"
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>

          {/* Differential Diagnosis */}
          <Card className="bg-gray-900 border-gray-700 lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-green-500">Differential Diagnosis</CardTitle>
              <CardDescription className="text-gray-400">Add possible diagnoses to consider</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={newDiagnosis}
                  onChange={(e) => setNewDiagnosis(e.target.value)}
                  placeholder="Enter a differential diagnosis"
                  className="bg-gray-800 border-gray-600 text-white"
                  onKeyPress={(e) => e.key === "Enter" && addDifferentialDiagnosis()}
                />
                <Button onClick={addDifferentialDiagnosis} className="bg-green-600 hover:bg-green-700">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {differentialDiagnosis.map((diagnosis, index) => (
                  <Badge key={index} variant="outline" className="border-gray-600 text-gray-300 pr-1">
                    {diagnosis}
                    <Button
                      variant="ghost"
                      size="sm"
                      className="ml-1 h-4 w-4 p-0 hover:bg-red-600"
                      onClick={() => removeDifferentialDiagnosis(index)}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Find Diagnosis Button */}
          <Card className="bg-gray-900 border-gray-700 lg:col-span-2">
            <CardContent className="pt-6">
              <Button
                onClick={findDiagnosis}
                className="w-full bg-green-600 hover:bg-green-700 text-lg py-6"
                disabled={isDiagnosing}
              >
                {isDiagnosing ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Finding Diagnosis...
                  </>
                ) : (
                  <>
                    <Brain className="mr-2 h-5 w-5" />
                    Find Diagnosis
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Diagnosis Result */}
          {diagnosisResult && (
            <Card className="bg-green-900 border-green-600 lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-green-400 flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Diagnosis Complete
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold text-white mb-2">Case ID</h4>
                  <p className="text-green-300">#{diagnosisResult.case_id}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-white mb-2">Final Diagnosis</h4>
                  <Badge className="bg-green-600 text-white">{diagnosisResult.final_diagnosis}</Badge>
                </div>
                <div>
                  <h4 className="font-semibold text-white mb-2">Reasoning</h4>
                  <p className="text-green-300">{diagnosisResult.reasoning}</p>
                </div>
                <Button
                  onClick={() => router.push(`/case/${diagnosisResult.case_id}`)}
                  className="w-full bg-green-600 hover:bg-green-700"
                >
                  View Complete Case
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Error Alert */}
          {error && (
            <Alert className="border-red-500 lg:col-span-2">
              <AlertDescription className="text-red-400">{error}</AlertDescription>
            </Alert>
          )}
        </div>
      </div>
    </div>
  )
}
