from app.ai.router.provider_setup import initialize_providers

def main():

    registry = initialize_providers()

    print("Registered providers:\n")

    for provider in registry.get_registered_provider_names():

        instance = registry.get_provider(provider)

        print("Provider:", provider)
        print("Configured:", instance.is_configured)
        print("-" * 40)


if __name__ == "__main__":
    main()
