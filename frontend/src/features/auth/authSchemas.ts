import { z } from "zod";

/**
 * Spec: login with ONE of username / national_id / phone / email + password
 * We keep the field name 'identifier' internally, but the UI label can be "Username / Email / Phone / National ID".
 */
export const loginSchema = z.object({
  identifier: z.string().trim().min(1, "Please enter username, email, phone, or national ID."),
  password: z.string().min(6, "Password must be at least 6 characters."),
});

export type LoginFormValues = z.infer<typeof loginSchema>;

export const signupSchema = z
  .object({
    username: z.string().trim().min(3, "Username is required (min 3 chars)."),
    firstName: z.string().trim().min(1, "First name is required."),
    lastName: z.string().trim().min(1, "Last name is required."),
    email: z.string().trim().email("Please enter a valid email."),
    phone: z.string().trim().min(5, "Phone is required."),
    nationalId: z.string().trim().min(3, "National ID is required."),
    password: z.string().min(6, "Password must be at least 6 characters."),
    confirmPassword: z.string().min(6, "Please confirm your password."),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match.",
    path: ["confirmPassword"],
  });

export type SignupFormValues = z.infer<typeof signupSchema>;
