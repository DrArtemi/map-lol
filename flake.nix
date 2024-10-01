{
  description = "Map LoL flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    pkgs = nixpkgs.legacyPackages.x86_64-linux;
  in 
  {
    devShells.x86_64-linux.default = pkgs.mkShell {
      packages = with pkgs; [
        python3
        python312Packages.plotly
        python312Packages.pandas
        python312Packages.pillow
        python312Packages.pydantic
      ];
    };
  };
}
