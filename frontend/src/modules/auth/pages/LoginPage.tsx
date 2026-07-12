import { motion } from "framer-motion";
import { Leaf, ShieldCheck } from "lucide-react";

import { APP_NAME } from "@/shared/constants/app";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/shared/components/ui/card";

import { LoginForm } from "../components/LoginForm";

export function LoginPage() {
  return (
    <div className="grid w-full max-w-5xl gap-6 lg:grid-cols-2 lg:gap-10">
      <motion.section
        initial={{ opacity: 0, x: -12 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.35 }}
        className="hidden flex-col justify-center rounded-2xl border bg-card p-8 shadow-sm lg:flex"
      >
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <Leaf className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">{APP_NAME}</h1>
            <p className="text-sm text-muted-foreground">Enterprise ESG Management Platform</p>
          </div>
        </div>

        <div className="space-y-4 text-sm text-muted-foreground">
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
            <p>Secure JWT authentication with role-based access control across all modules.</p>
          </div>
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
            <p>Session handling with refresh tokens, protected routes, and activity logging.</p>
          </div>
        </div>
      </motion.section>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="w-full"
      >
        <Card className="border shadow-sm transition-shadow hover:shadow-md">
          <CardHeader className="space-y-2 text-center sm:text-left">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary sm:mx-0">
              <Leaf className="h-6 w-6" />
            </div>
            <CardTitle className="text-2xl sm:text-3xl">Sign in</CardTitle>
            <CardDescription>
              Access your EcoSphere workspace with your organization credentials.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <LoginForm />
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
