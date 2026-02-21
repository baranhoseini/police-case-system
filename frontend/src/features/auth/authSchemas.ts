import { z } from "zod";

export const loginSchema = z.object({
  identifier: z.string().min(1, "Identifier is required."),
  password: z.string().min(1, "Password is required."),
});

export const signupSchema = z
  .object({
    username: z.string().min(3, "Username is required."),
    firstName: z.string().min(1, "First name is required."),
    lastName: z.string().min(1, "Last name is required."),
    email: z.string().email("Please enter a valid email."),
    phone: z.string().min(5, "Phone is required."),
    nationalId: z.string().min(5, "National ID is required."),
    password: z.string().min(8, "Password must be at least 8 characters."),
    confirmPassword: z.string().min(8, "Please confirm your password."),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match.",
    path: ["confirmPassword"],
  });

export type LoginFormValues = z.infer<typeof loginSchema>;
export type SignupFormValues = z.infer<typeof signupSchema>;