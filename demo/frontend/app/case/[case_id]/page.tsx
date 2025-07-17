"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ArrowLeft, User, FileText, Stethoscope, TestTube, Microscope, Brain } from "lucide-react"
import { API_ENDPOINTS } from "@/lib/config"

interface Case {
  id: number
  user_id: string
  name: string
  age: number
  chief_complaint: string
  previous_medical_history?: string
  imageological_examination?: string
  laboratory_examination?: string
  pathological_examination?: string
  differential_diagnosis: string[]
  final_diagnosis?: string
  reasoning?: string
}

export default function CaseDetailPage({ params }: { params: { case_id: string } }) {
  const [caseData, setCaseData] = useState<Case | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const { case_id } = params

  useEffect(() => {
    fetchCase()
  }, [case_id])

  const fetchCase = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.CASE(case_id))
      if (response.ok) {
        const data = await response.json()
        setCaseData(data)
      }
    } catch (error) {
      console.error("Error fetching case:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleBack = () => {
    const user_id = localStorage.getItem("user_id")
    if (user_id) {
      router.push(`/cases/${user_id}`)
    } else {
      router.push("/login")
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-green-500">Loading case details...</div>
      </div>
    )
  }

  if (!caseData) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-red-500 mb-4">Case not found</h2>
          <Button onClick={handleBack} className="bg-green-600 hover:bg-green-700">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Cases
          </Button>
        </div>
      </div>
    )
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
            <h1 className="text-3xl font-bold text-green-500">Case #{caseData.id}</h1>
            <p className="text-gray-400">Detailed case information</p>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Patient Information */}
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-green-500 flex items-center gap-2">
                <User className="h-5 w-5" />
                Patient Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold text-white mb-2">Name</h4>
                <p className="text-gray-300">{caseData.name}</p>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-2">Age</h4>
                <p className="text-gray-300">{caseData.age} years old</p>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-2">Chief Complaint</h4>
                <p className="text-gray-300">{caseData.chief_complaint}</p>
              </div>
            </CardContent>
          </Card>

          {/* Medical History */}
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-green-500 flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Medical History
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-300">
                {caseData.previous_medical_history || "No previous medical history recorded"}
              </p>
            </CardContent>
          </Card>

          {/* Examinations */}
          <Card className="bg-gray-900 border-gray-700 lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-green-500 flex items-center gap-2">
                <Stethoscope className="h-5 w-5" />
                Examinations
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {caseData.imageological_examination && (
                <div>
                  <h4 className="font-semibold text-white mb-2 flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    Imageological Examination
                  </h4>
                  <p className="text-gray-300">{caseData.imageological_examination}</p>
                </div>
              )}

              {caseData.laboratory_examination && (
                <>
                  <Separator className="bg-gray-700" />
                  <div>
                    <h4 className="font-semibold text-white mb-2 flex items-center gap-2">
                      <TestTube className="h-4 w-4" />
                      Laboratory Examination
                    </h4>
                    <p className="text-gray-300">{caseData.laboratory_examination}</p>
                  </div>
                </>
              )}

              {caseData.pathological_examination && (
                <>
                  <Separator className="bg-gray-700" />
                  <div>
                    <h4 className="font-semibold text-white mb-2 flex items-center gap-2">
                      <Microscope className="h-4 w-4" />
                      Pathological Examination
                    </h4>
                    <p className="text-gray-300">{caseData.pathological_examination}</p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Differential Diagnosis */}
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-green-500 flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Differential Diagnosis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {caseData.differential_diagnosis.map((diagnosis, index) => (
                  <Badge key={index} variant="outline" className="border-gray-600 text-gray-300">
                    {diagnosis}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Final Diagnosis & Reasoning */}
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-green-500">Final Diagnosis & Reasoning</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {caseData.final_diagnosis ? (
                <>
                  <div>
                    <h4 className="font-semibold text-white mb-2">Final Diagnosis</h4>
                    <Badge className="bg-green-600 text-white">{caseData.final_diagnosis}</Badge>
                  </div>
                  {caseData.reasoning && (
                    <div>
                      <h4 className="font-semibold text-white mb-2">Reasoning</h4>
                      <p className="text-gray-300">{caseData.reasoning}</p>
                    </div>
                  )}
                </>
              ) : (
                <p className="text-gray-400 italic">No final diagnosis available yet</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
