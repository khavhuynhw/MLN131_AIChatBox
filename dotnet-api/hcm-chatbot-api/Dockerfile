# -------------------------------
# Base runtime
# -------------------------------
    FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
    WORKDIR /app
    EXPOSE 5000
    
    # -------------------------------
    # Build stage
    # -------------------------------
    FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
    WORKDIR /src
    
    # 🧱 Copy từng project riêng để tận dụng cache
    COPY ["Data/Data.csproj", "Data/"]
    COPY ["Models/Models.csproj", "Models/"]
    COPY ["Repositories/Repositories.csproj", "Repositories/"]
    COPY ["Services/Services.csproj", "Services/"]
    COPY ["Web_API/Web_API.csproj", "Web_API/"]
    
    # 🧩 Restore dependencies
    RUN dotnet restore "Web_API/Web_API.csproj"
    
    # 📂 Copy toàn bộ source code
    COPY . .
    
    # 🏗️ Build project chính
    RUN dotnet build "Web_API/Web_API.csproj" -c Release --no-restore
    
    # -------------------------------
    # Publish stage
    # -------------------------------
    FROM build AS publish
    RUN dotnet publish "Web_API/Web_API.csproj" -c Release -o /app/publish --no-build
    
    # -------------------------------
    # Runtime stage
    # -------------------------------
    FROM base AS final
    WORKDIR /app
    COPY --from=publish /app/publish .
    
    ENV ASPNETCORE_ENVIRONMENT=Production
    ENV ASPNETCORE_URLS=http://+:5000
    
    ENTRYPOINT ["dotnet", "Web_API.dll"]
    