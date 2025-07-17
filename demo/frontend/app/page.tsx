"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function HomePage() {
  const router = useRouter()

  useEffect(() => {
    // Check if user is already logged in
    const user_id = localStorage.getItem("user_id")
    if (user_id) {
      router.push(`/cases/${user_id}`)
    } else {
      router.push("/login")
    }
  }, [router])

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-green-500">Loading...</div>
    </div>
  )
}
