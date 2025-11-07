import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';
import { Base } from '../profile/schemas';
import { renderEnv } from './render-env';

export function applyProfile(profileName: string, root: string, templatePath: string) {
  const defaultsDir = path.join(root, 'core', 'installer', 'profile', 'defaults');
  const profilePath = path.join(defaultsDir, `${profileName}.yaml`);
  if (!fs.existsSync(profilePath)) {
    throw new Error(`unknown profile: ${profileName}`);
  }
  const parsed = YAML.parse(fs.readFileSync(profilePath, 'utf8'));
  const profile = Base.parse(parsed);
  const vars = {
    AION_PROFILE: profile.name,
    AION_GATEWAY: String(profile.services.gateway),
    AION_CONTROL: String(profile.services.control),
    AION_CONSOLE: String(profile.services.console),
  };
  renderEnv(templatePath, path.join(root, '.env'), vars);
  return profile;
}
