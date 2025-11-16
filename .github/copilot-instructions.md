# AI Rules for tinyurl.serafin.tech

See application description in [docs/REQUIREMENTS.md](../docs/REQUIREMENTS.md).

## CODING_PRACTICES

### Guidelines for SUPPORT_LEVEL

#### SUPPORT_EXPERT

- Favor elegant, maintainable solutions over verbose code. Assume understanding of language idioms and design patterns.
- Highlight potential performance implications and optimization opportunities in suggested code.
- Frame solutions within broader architectural contexts and suggest design alternatives when appropriate.
- Focus comments on 'why' not 'what' - assume code readability through well-named functions and variables.
- Proactively address edge cases, race conditions, and security considerations without being prompted.
- When debugging, provide targeted diagnostic approaches rather than shotgun solutions.
- Suggest comprehensive testing strategies rather than just example tests, including considerations for mocking, test organization, and coverage.


### Guidelines for VERSION_CONTROL

#### GIT

- Use conventional commits to create meaningful commit messages
- Use feature branches with descriptive names following [branch naming convention](../docs/branch-naming-convention.md)
- Write meaningful commit messages that explain why changes were made, not just what
- Keep commits focused on single logical changes to facilitate code review and bisection
- Use interactive rebase to clean up history before merging feature branches
- Leverage git hooks to enforce code quality checks before commits and pushes

#### GITHUB

- Use pull request templates to standardize information provided for code reviews
- Implement branch protection rules for `main` branch to enforce quality checks
- Configure required status checks to prevent merging code that fails tests or linting
- Use GitHub Actions for CI/CD workflows to automate testing and deployment

### Guidelines for ARCHITECTURE

#### CLEAN_ARCHITECTURE

- Strictly separate code into layers: entities, use cases, interfaces, and frameworks
- Ensure dependencies point inward, with inner layers having no knowledge of outer layers
- Implement domain entities that encapsulate business rules srecified in [requirements](../docs/REQUIREMENTS.md) without framework dependencies
- Use interfaces (ports) and implementations (adapters) to isolate external dependencies
- Create use cases that orchestrate entity interactions for specific business operations
- Implement mappers to transform data between layers to maintain separation of concerns

#### MONOREPO

- Configure workspace-aware tooling to optimize build and test processes
- Implement clear package boundaries with explicit dependencies between packages
- Use consistent versioning strategy across all packages (independent or lockstep)
- Configure CI/CD to build and test only affected packages for efficiency
- Implement shared configurations for linting, testing, and {{development_tooling}}
- Use code generators to maintain consistency across similar packages or modules

## FRONTEND

### Guidelines for SVELTE

#### SVELTE_CODING_STANDARDS

- Use runes for $state, $effect and $props management instead of the $ prefix
- Use the $ prefix for reactive store values instead of manual store subscription
- Use slot props for better component composition
- Leverage the :global() modifier sparingly for global CSS
- Implement Svelte transitions and animations for smooth UI changes
- Use $effect rune for derived state
- Use simple callback props instead of createEventDispatcher
- Use lifecycle functions (onMount, onDestroy) for setup and cleanup
- Leverage special elements like <svelte:window> and <svelte:component> for dynamic behavior

#### SVELTE_KIT

- Use server-side load functions to fetch data before rendering pages
- Implement form actions for handling form submissions with progressive enhancement
- Use page stores ($page) to access route parameters and other page data
- Leverage SvelteKit's server-only modules for sensitive operations
- Implement +error.svelte files for custom error handling at the route level
- Use the enhance function for progressive enhancement of forms
- Leverage SvelteKit hooks for global middleware functionality
- Implement route groups (folders with parentheses) for logical organization without URL impact
- Use the new Embedded SvelteKit plugin system
- Implement content negotiation with accept header in load functions

## BACKEND

### Guidelines for PYTHON

#### FASTAPI

- Use Pydantic models for request and response validation with strict type checking and custom validators
- Implement dependency injection for services and database sessions to improve testability and resource management
- Use async endpoints for I/O-bound operations to improve throughput for {{high_load_endpoints}}
- Leverage FastAPI's background tasks for non-critical operations that don't need to block the response
- Implement proper exception handling with HTTPException and custom exception handlers for {{error_scenarios}}
- Use path operation decorators consistently with appropriate HTTP methods (GET for retrieval, POST for creation, etc.)

## DATABASE

### Guidelines for SQLite

#### SQLITE_BEST_PRACTICES

- Use WAL (Write-Ahead Logging) mode for better concurrency in read-heavy applications
- Implement proper indexing strategies on frequently queried columns to optimize read performance
- Use parameterized queries to prevent SQL injection attacks
- Regularly vacuum the database to reclaim unused space and optimize performance
- Use transactions for batch operations to ensure atomicity and improve performance
- Normalize database schema to reduce redundancy and improve data integrity
- Implement foreign key constraints to maintain referential integrity between tables

## DEVOPS

### Guidelines for CONTAINERIZATION

#### DOCKER

- Use multi-stage builds to create smaller production images
- Implement layer caching strategies to speed up builds for {{dependency_types}}
- Use non-root users in containers for better security
- Leverage Docker Compose for local development environments with multiple services
- Use .dockerignore files to exclude unnecessary files from the build context

## TESTING

### Guidelines for UNIT

#### PYTEST

- Use fixtures for test setup and dependency injection
- Implement parameterized tests for testing multiple inputs for {{function_types}}
- Use monkeypatch for mocking dependencies
