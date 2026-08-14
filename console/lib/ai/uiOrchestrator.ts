import { z } from 'zod';
import { PageSchema } from '../schemaLoader';

export type UiContext = {
  role: string;
  featureFlags: string[];
  tenancyMode: 'single' | 'multi';
  tenantId?: string;
  setupDone?: boolean;
  onboardingComplete?: boolean;
};

const criticalRoutes = ['/setup', '/onboarding', '/agents/catalog', '/agents/my-agents'];

const fieldSchema = z.object({
  name: z.string(),
  label: z.string().optional(),
  type: z.string(),
  required: z.boolean().optional(),
  default: z.any().optional(),
  placeholder: z.string().optional(),
  visibilityRules: z.any().optional()
});

const patchSchema = z.object({
  navPatch: z
    .object({
      reorder: z.array(z.string()).optional(),
      hide: z.array(z.string()).optional(),
      add: z.array(z.any()).optional()
    })
    .optional(),
  pagePatch: z
    .object({
      addFields: z.array(fieldSchema).optional(),
      removeFields: z.array(z.string()).optional(),
      addComponents: z.array(z.any()).optional(),
      removeComponents: z.array(z.string()).optional()
    })
    .optional(),
  rationale: z.string().optional()
});

export type UiPatch = z.infer<typeof patchSchema>;

export function validatePatch(patch: UiPatch) {
  patchSchema.parse(patch);
  if (patch.navPatch?.hide) {
    for (const route of patch.navPatch.hide) {
      if (criticalRoutes.includes(route)) {
        throw new Error('AI patch attempted to hide a critical flow');
      }
    }
  }
  if (patch.pagePatch?.addFields) {
    for (const field of patch.pagePatch.addFields) {
      if (/(secret|token|key|password|private)/i.test(field.name) && field.type !== 'password') {
        throw new Error(`Field ${field.name} would expose a secret`);
      }
    }
  }
}

export function applyPatch(base: PageSchema, patch?: UiPatch): PageSchema {
  if (!patch) return base;
  validatePatch(patch);
  const next = { ...base, sections: [...base.sections] };
  if (patch.pagePatch?.addComponents && next.sections.length > 0) {
    next.sections[0].components = [...(next.sections[0].components ?? []), ...patch.pagePatch.addComponents];
  }
  if (patch.pagePatch?.addFields) {
    for (const section of next.sections) {
      for (const component of section.components ?? []) {
        if (component.fields) {
          component.fields.push(...patch.pagePatch.addFields);
        }
      }
    }
  }
  return next;
}

export async function getAiPatch(): Promise<UiPatch | null> {
  return null;
}

export async function orchestratePage(schema: PageSchema, context: UiContext): Promise<PageSchema> {
  void context;
  const patch = await getAiPatch();
  if (!patch) return schema;
  return applyPatch(schema, patch);
}
