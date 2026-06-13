# Mini App to Farcaster App Migration Checklist

## Pre-Migration

- [ ] Audit current mini app dependencies
- [ ] Document all API endpoints used
- [ ] Identify Farcaster SDK features needed
- [ ] Set up development environment

## Migration Steps

1. **Update package.json**
   - Replace mini app SDK with @farcaster/* packages
   - Update build scripts

2. **Update authentication**
   - Migrate to Farcaster Auth Client
   - Update sign-in flow

3. **Update frame handlers**
   - Migrate to new frame message format
   - Update state management

4. **Test thoroughly**
   - Verify all button actions work
   - Test input handling
   - Check state persistence

## Post-Migration

- [ ] Run validation script
- [ ] Test in Farcaster client
- [ ] Update documentation
- [ ] Deploy to production
