import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Input } from '@/components/common/Input';
import { Button } from '@/components/common/Button';
import { ShieldCheck, Lock, User, AlertCircle } from 'lucide-react';

const loginSchema = z.object({
  username_or_email: z.string().min(3, 'Username or email is required'),
  password: z.string().min(4, 'Password must be at least 4 characters'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username_or_email: 'admin',
      password: 'Admin@123456',
    },
  });

  const onSubmit = async (data: LoginFormValues) => {
    setError(null);
    setIsLoading(true);
    try {
      await login(data);
      navigate('/dashboard');
    } catch (err: any) {
      setError(
        err.response?.data?.message || 'Authentication failed. Please check your credentials.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const setDemoCredentials = () => {
    setValue('username_or_email', 'admin');
    setValue('password', 'Admin@123456');
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background p-4 relative overflow-hidden">
      {/* Background ambient gradient glow */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-primary/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        <div className="bg-card border border-border rounded-2xl shadow-2xl p-8 backdrop-blur-xl">
          {/* Brand header */}
          <div className="flex flex-col items-center text-center mb-8">
            <div className="p-3.5 bg-primary/10 border border-primary/20 rounded-2xl text-primary mb-3 shadow-inner">
              <ShieldCheck className="w-8 h-8" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              EMP CONTROL PORTAL
            </h1>
            <p className="text-xs text-muted-foreground mt-1">
              Windows Agent Management & Workforce Monitoring
            </p>
          </div>

          {error && (
            <div className="mb-5 p-3.5 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Username or Email"
              placeholder="e.g. admin or admin@acme.corp"
              leftIcon={<User className="w-4 h-4" />}
              error={errors.username_or_email?.message}
              {...register('username_or_email')}
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
              error={errors.password?.message}
              {...register('password')}
            />

            <div className="pt-2">
              <Button type="submit" className="w-full py-2.5" isLoading={isLoading}>
                Sign In to Console
              </Button>
            </div>
          </form>

          {/* Demo hint */}
          <div className="mt-6 pt-6 border-t border-border/80 flex items-center justify-between text-xs text-muted-foreground">
            <span>Demo: <strong className="text-foreground">admin</strong> / <strong className="text-foreground">Admin@123456</strong></span>
            <button
              type="button"
              onClick={setDemoCredentials}
              className="text-primary hover:underline font-medium focus:outline-none"
            >
              Fill Credentials
            </button>
          </div>
        </div>

        <p className="text-center text-[11px] text-muted-foreground mt-6 font-mono">
          Phase 1 Architecture Foundation • Zero-Trust Enrolled Endpoints
        </p>
      </div>
    </div>
  );
};
