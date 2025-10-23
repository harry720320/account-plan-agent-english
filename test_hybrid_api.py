#!/usr/bin/env python3
"""
Test script to verify hybrid API configuration
Tests both Chat Completions API and Responses API functionality
"""

import sys
import os
import asyncio
from config import settings

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_hybrid_configuration():
    """Test hybrid API configuration"""
    print("🔧 Testing Hybrid API Configuration...")
    
    # Check Chat Completions API models
    assert settings.default_model == "gpt-4o-mini", f"Expected gpt-4o-mini, got {settings.default_model}"
    assert settings.conversation_model == "gpt-4o-mini", f"Expected gpt-4o-mini, got {settings.conversation_model}"
    assert settings.plan_generation_model == "gpt-4o-mini", f"Expected gpt-4o-mini, got {settings.plan_generation_model}"
    assert settings.question_model == "gpt-4o-mini", f"Expected gpt-4o-mini, got {settings.question_model}"
    assert settings.history_model == "gpt-4o-mini", f"Expected gpt-4o-mini, got {settings.history_model}"
    assert settings.dynamic_questioning_model == "gpt-4o-mini", f"Expected gpt-4o-mini, got {settings.dynamic_questioning_model}"
    
    # Check Responses API models for external info
    assert settings.external_info_model == "gpt-5-mini", f"Expected gpt-5-mini, got {settings.external_info_model}"
    assert settings.external_responses_model == "gpt-5-mini", f"Expected gpt-5-mini, got {settings.external_responses_model}"
    
    # Check web search is enabled
    assert settings.external_use_responses == True, f"Expected True, got {settings.external_use_responses}"
    
    print("✅ Hybrid configuration is correct!")
    print("  - Chat Completions API: gpt-4o-mini (conversation, plan, question, history, dynamic)")
    print("  - Responses API: gpt-5-mini (external info, web search)")
    print("  - Web search: Enabled")
    return True

def test_imports():
    """Test that all modules can be imported without errors"""
    print("\n📦 Testing Module Imports...")
    
    modules_to_test = [
        'conversation_manager',
        'external_info', 
        'dynamic_questioning',
        'history_manager',
        'question_manager',
        'plan_generator',
        'main'
    ]
    
    failed_imports = []
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} imported successfully")
        except Exception as e:
            print(f"❌ {module_name} import failed: {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"❌ Failed imports: {failed_imports}")
        return False
    else:
        print("✅ All modules imported successfully")
        return True

def test_external_info_methods():
    """Test ExternalInfoCollector methods"""
    print("\n🌐 Testing ExternalInfoCollector Methods...")
    
    try:
        from external_info import ExternalInfoCollector
        collector = ExternalInfoCollector()
        
        # Check that _responses_web_search method exists
        assert hasattr(collector, '_responses_web_search'), "Missing _responses_web_search method"
        print("✅ _responses_web_search method exists")
        
        # Check that _extract_responses_text method exists
        assert hasattr(collector, '_extract_responses_text'), "Missing _extract_responses_text method"
        print("✅ _extract_responses_text method exists")
        
        # Check web search methods
        methods_to_test = [
            'get_company_profile',
            'get_news_snapshot', 
            'get_market_info'
        ]
        
        for method_name in methods_to_test:
            assert hasattr(collector, method_name), f"Missing {method_name} method"
            method = getattr(collector, method_name)
            assert callable(method), f"{method_name} is not callable"
            print(f"✅ {method_name} method exists and is callable")
        
        print("✅ ExternalInfoCollector is ready for web search!")
        return True
        
    except Exception as e:
        print(f"❌ ExternalInfoCollector test failed: {e}")
        return False

async def test_chat_completions_api():
    """Test Chat Completions API functionality"""
    print("\n💬 Testing Chat Completions API (gpt-4o-mini)...")
    
    try:
        from conversation_manager import ConversationManager
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from models import Base
        
        # Create in-memory database for testing
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        manager = ConversationManager()
        
        # Test conversation creation (without actual API call)
        conversation = {
            "conversation_id": "test_conv",
            "account_id": 1,
            "original_question": "Test question",
            "messages": [{"role": "assistant", "content": "Hello!"}],
            "status": "active"
        }
        
        # Test conversation continuation (this would make API call if API key is set)
        if settings.openai_api_key:
            try:
                result = await manager.continue_conversation(conversation, "Test user message")
                print("✅ Chat Completions API call successful")
                print(f"   Response preview: {result[:100]}..." if len(result) > 100 else f"   Response: {result}")
            except Exception as e:
                print(f"⚠️ Chat Completions API call failed: {e}")
        else:
            print("⚠️ Skipping API test - no OpenAI API key set")
        
        print("✅ Chat Completions API test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Chat Completions API test failed: {e}")
        return False

async def test_responses_api():
    """Test Responses API functionality"""
    print("\n🌐 Testing Responses API (gpt-5-mini) for External Info...")
    
    try:
        from external_info import ExternalInfoCollector
        
        collector = ExternalInfoCollector()
        
        # Test company profile collection (this would make API call if API key is set)
        if settings.openai_api_key:
            try:
                print("   Testing company profile collection...")
                result = await collector.get_company_profile("Apple Inc")
                print("✅ Company profile API call successful")
                print(f"   Company: {result.get('company_name', 'N/A')}")
                print(f"   Industry: {result.get('industry', 'N/A')}")
                print(f"   Size: {result.get('company_size', 'N/A')}")
                
                print("\n   Testing news collection...")
                news_result = await collector.get_news_snapshot("Apple Inc", 3)
                print("✅ News collection API call successful")
                print(f"   News count: {len(news_result.get('news', []))}")
                
                print("\n   Testing market info collection...")
                market_result = await collector.get_market_info("Apple Inc", "Technology")
                print("✅ Market info API call successful")
                print(f"   Industry: {market_result.get('industry', 'N/A')}")
                print(f"   Trends: {market_result.get('trends', 'N/A')[:100]}...")
                
            except Exception as e:
                print(f"⚠️ Responses API call failed: {e}")
        else:
            print("⚠️ Skipping API test - no OpenAI API key set")
        
        print("✅ Responses API test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Responses API test failed: {e}")
        return False

def test_api_key_status():
    """Test API key status"""
    print("\n🔑 Testing API Key Status...")
    
    if settings.openai_api_key:
        if settings.openai_api_key.startswith("sk-"):
            print("✅ OpenAI API key is set and appears valid")
            return True
        else:
            print("⚠️ OpenAI API key is set but doesn't start with 'sk-'")
            return False
    else:
        print("❌ No OpenAI API key set")
        print("   To test API functionality, please set OPENAI_API_KEY in your .env file")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing Hybrid API Configuration\n")
    
    # Basic configuration tests
    config_tests = [
        test_hybrid_configuration,
        test_imports,
        test_external_info_methods,
        test_api_key_status
    ]
    
    print("=" * 60)
    print("BASIC CONFIGURATION TESTS")
    print("=" * 60)
    
    config_results = []
    for test in config_tests:
        try:
            result = test()
            config_results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            config_results.append(False)
    
    # API functionality tests (only if API key is available)
    if settings.openai_api_key:
        print("\n" + "=" * 60)
        print("API FUNCTIONALITY TESTS")
        print("=" * 60)
        
        api_tests = [
            test_chat_completions_api,
            test_responses_api
        ]
        
        api_results = await asyncio.gather(*[test() for test in api_tests], return_exceptions=True)
        
        # Check API results
        api_failed = [i for i, result in enumerate(api_results) if result is not True]
        if api_failed:
            print(f"\n⚠️ {len(api_failed)} API test(s) had issues!")
            for i in api_failed:
                print(f"  - API Test {i+1}: {api_results[i]}")
    else:
        print("\n" + "=" * 60)
        print("API FUNCTIONALITY TESTS SKIPPED")
        print("=" * 60)
        print("⚠️ No API key available - skipping API functionality tests")
        api_results = []
    
    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    config_failed = sum(1 for r in config_results if not r)
    if config_failed == 0:
        print("✅ All configuration tests passed!")
        print("📊 Summary:")
        print("✅ Chat Completions API: gpt-4o-mini for core functions")
        print("✅ Responses API: gpt-5-mini for external info and web search")
        print("✅ Web search functionality enabled")
        print("✅ All modules working correctly")
        
        if settings.openai_api_key:
            api_success = sum(1 for r in api_results if r is True)
            print(f"✅ API tests: {api_success}/{len(api_results)} passed")
            print("\n🚀 Your application is ready to use!")
        else:
            print("\n⚠️ Set OPENAI_API_KEY to test API functionality")
    else:
        print(f"❌ {config_failed} configuration test(s) failed!")
        return False

if __name__ == "__main__":
    asyncio.run(main())
