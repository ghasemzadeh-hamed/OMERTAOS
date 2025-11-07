import fs from 'node:fs';

export function renderEnv(templatePath: string, outPath: string, vars: Record<string, string>) {
  let template = fs.readFileSync(templatePath, 'utf8');
  for (const [key, value] of Object.entries(vars)) {
    template = template.replaceAll(`\${${key}}`, value);
  }
  fs.writeFileSync(outPath, template, 'utf8');
}
