// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import "forge-ctf/CTFDeployer.sol";
import "forge-ctf/CTFChallenge.sol";

import "src/PerformancePointATM.sol";

contract Deploy is CTFDeployer {
    function deploy(address system, address player) internal override returns (CTFChallenge[] memory challenges) {
        vm.startBroadcast(system);

        PerformancePointHelper helper = new PerformancePointHelper();
        PerformancePointATM atm = new PerformancePointATM{value: 10 ether}(address(helper));

        challenges = new CTFChallenge[](1);
        challenges[0] = CTFChallenge("PerformancePointATM", address(atm));

        vm.stopBroadcast();
    }
}
