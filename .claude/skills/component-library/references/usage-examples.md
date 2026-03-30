# Component Usage Examples

Real patterns from Wythm screens, organized by complexity.

## Basic Patterns

### Auth Form (Input + Button)

```tsx
import { Button } from "@/shared/ui/common/Button";
import { Input } from "@/shared/ui/common/Input";

function SignInScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

  return (
    <View style={styles.container}>
      <Input
        label="Email"
        value={email}
        onChangeText={setEmail}
        error={errors.email}
        required
        keyboardType="email-address"
        autoCapitalize="none"
        autoComplete="email"
      />
      <Input
        label="Password"
        value={password}
        onChangeText={setPassword}
        error={errors.password}
        required
        secureTextEntry
        autoComplete="current-password"
      />
      <Button
        title="Sign In"
        onPress={handleSignIn}
        loading={isLoading}
        fullWidth
      />
    </View>
  );
}
```

### Loading State → Content

```tsx
import { LoadingView } from "@/shared/ui/common/loaders/LoadingView";

function ScreenWithLoading() {
  const { isLoading, data } = useData();
  if (isLoading) return <LoadingView />;
  return <Content data={data} />;
}
```

### Destructive Action

```tsx
<Button title="Delete Account" variant="danger" onPress={showDeleteConfirmation} />
```

### Ghost / Link Action

```tsx
<Button title="Forgot password?" variant="ghost" size="small" onPress={handleForgotPassword} />
```

### Typography Hierarchy

```tsx
import { StyledText } from "@/shared/ui/StyledText";

<StyledText variant="h2">Screen Title</StyledText>
<StyledText variant="body">Main content paragraph goes here.</StyledText>
<StyledText variant="caption" colorToken="secondary">Updated 2 hours ago</StyledText>
<StyledText variant="label" bold>Field Label</StyledText>
```

### Toast Notifications

```tsx
import { useToastStore } from "@/store";

function SaveButton() {
  const { addToast } = useToastStore();

  const handleSave = async () => {
    try {
      await saveData();
      addToast({ type: "success", title: "Saved!", message: "Your changes were saved." });
    } catch {
      addToast({ type: "error", title: "Save failed", message: "Please try again." });
    }
  };

  return <Button title="Save" onPress={handleSave} />;
}
```

## Composition Patterns

### Form inside Bottom Sheet

```tsx
import { AppBottomSheet } from "@/shared/ui/common/AppBottomSheet";
import { Button } from "@/shared/ui/common/Button";
import { Input } from "@/shared/ui/common/Input";
import { StyledText } from "@/shared/ui/StyledText";

function EditProfileSheet({ visible, onClose }: { visible: boolean; onClose: () => void }) {
  const [name, setName] = useState("");
  const [saving, setSaving] = useState(false);

  return (
    <AppBottomSheet visible={visible} onClose={onClose} size="md">
      <View style={{ padding: 16, gap: 12 }}>
        <StyledText variant="h3">Edit Profile</StyledText>
        <Input label="Display Name" value={name} onChangeText={setName} required />
        <Button title="Save" onPress={handleSave} loading={saving} fullWidth />
        <Button title="Cancel" variant="ghost" onPress={onClose} fullWidth />
      </View>
    </AppBottomSheet>
  );
}
```

### Screen with Loading → Content → Actions

```tsx
import { LoadingView } from "@/shared/ui/common/loaders/LoadingView";
import { StyledText } from "@/shared/ui/StyledText";
import { Button } from "@/shared/ui/common/Button";

function DetailScreen() {
  const { isLoading, data } = useData();
  if (isLoading) return <LoadingView />;

  return (
    <View style={{ flex: 1, padding: 16, gap: 12 }}>
      <StyledText variant="h2">{data.title}</StyledText>
      <StyledText variant="body">{data.description}</StyledText>
      <StyledText variant="caption" colorToken="secondary">
        Last updated {data.updatedAt}
      </StyledText>

      <View style={{ marginTop: "auto", gap: 8 }}>
        <Button title="Continue" onPress={handleNext} fullWidth />
        <Button title="Skip for now" variant="ghost" size="small" onPress={handleSkip} />
      </View>
    </View>
  );
}
```

### Confirmation Bottom Sheet (Destructive Action)

```tsx
function DeleteConfirmSheet({ visible, onClose, onConfirm }: Props) {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await onConfirm();
      onClose();
    } finally {
      setDeleting(false);
    }
  };

  return (
    <AppBottomSheet visible={visible} onClose={onClose} size="sm">
      <View style={{ padding: 16, gap: 12, alignItems: "center" }}>
        <StyledText variant="h3">Delete Item?</StyledText>
        <StyledText variant="body" colorToken="secondary">
          This action cannot be undone.
        </StyledText>
        <Button title="Delete" variant="danger" onPress={handleDelete} loading={deleting} fullWidth />
        <Button title="Cancel" variant="secondary" onPress={onClose} fullWidth />
      </View>
    </AppBottomSheet>
  );
}
```

### Language Selector Usage

```tsx
import { LanguageSelector } from "@/shared/ui/common/LanguageSelector";

function SettingsScreen() {
  const [showLangPicker, setShowLangPicker] = useState(false);

  return (
    <View>
      <Button title="Change Language" variant="secondary" onPress={() => setShowLangPicker(true)} />
      <LanguageSelector visible={showLangPicker} onClose={() => setShowLangPicker(false)} />
    </View>
  );
}
```

## Form Validation Pattern

```tsx
function ValidatedForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!email) newErrors.email = "Email is required";
    if (!password) newErrors.password = "Password is required";
    if (password && password.length < 8) newErrors.password = "Must be at least 8 characters";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  return (
    <View style={{ gap: 12 }}>
      <Input label="Email" error={errors.email} value={email} onChangeText={setEmail} required />
      <Input label="Password" error={errors.password} value={password} onChangeText={setPassword} required secureTextEntry />
      <Button title="Submit" onPress={() => validate() && submit()} fullWidth />
    </View>
  );
}
```
