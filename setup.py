import setuptools

setuptools.setup(
    name="skywrangler-web-server",
    version="1.4.4",
    author="David Lechner",
    author_email="david@ablerobots.com",
    description="Sky Wrangler onboard computer web server",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=["aiohttp", "aiohttp-sse", "dbus-next", "mavsdk", "sdnotify"],
    entry_points={
        "console_scripts": [
            "skywrangler-web-server = skywrangler_web_server.__main__:main"
        ]
    },
)
